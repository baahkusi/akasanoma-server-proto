from io import BytesIO
import datetime
import pandas as pd
from .db import User, Login, Entry, Translation, Validation, DataBaseMappings,db
from .utils import fresh_pin, send_email, token, get_data, pay_user, points_to_amount
from .decors import login_required
from datauri import DataURI

BATCH = 5


def register(req, **kwargs):
    """
    :kwargs: email, device, user_type
    """

    try:

        user = User.create(email=kwargs['email'],
                           user_type=kwargs['user_type'])

        if user.user_type == 'client':
            login = Login.create(user=user.id, device=kwargs['device'])
            login.pin = int(f"{fresh_pin()}{login.id}")
            login.save()
            message = f'<strong>Login code {login.pin}</strong>'
        else:
            message = f'''You got an invitation to be a<strong> {user.user_type} @Akasanoma</strong>. 
                            Go to <a href="http://akasanoma.surge.sh">Akasanoma Login.</a> 
                            "Testing Initial Dashboard, kindly try it out and give feedback"'''
        send_email(kwargs['email'], message)

    except Exception as e:
        return {'status': False, 'data': repr(e)}

    return {'status': True, 'data': ''}


def login(req, **kwargs):
    """
    :kwargs: email, fresh_pin, device
    """
    try:

        user = User.get(email=kwargs['email'])
        login = Login.get(
            user=user.id, pin=kwargs['fresh_pin'], device=kwargs['device'])

        if login.token:
            return {'status': False, 'data': 'Pin already used'}

        message = f'<strong>Login code {login.pin}</strong>'
        login.token = token(kwargs['email'], message)
        login.save()

    except Exception as e:
        return {'status': False, 'data': repr(e)}

    return {'status': True, 'data': {'token': login.token, 'user_type': login.user.user_type, 'user_points':login.user.points, 'user_level':login.user.level}}


def generate_pin(req, **kwargs):
    """
    :kwargs: email, device
    """
    try:

        user = User.get(email=kwargs['email'])
        login = Login.create(user=user.id, device=kwargs['device'])
        login.pin = int(f"{fresh_pin()}{login.id}")
        login.save()
        message = f'<strong>Login code {login.pin}</strong>'
        send_email(kwargs['email'], message)

    except Exception as e:
        return {'status': False, 'data': repr(e)}

    return {'status': True, 'data': ''}


@login_required
def redeem_points(req, **kwargs):
    """
    :kwargs: phone
    """
    try:

        amount = points_to_amount(req.user.points)

        if not pay_user(amount, kwargs['phone']):
            return {'status': False, 'data': 'Could Not pay user'}

        User.update(points = 0).where(User.id==req.user.id)

    except Exception as e:
        return {'status': False, 'data': repr(e)}

    return {'status': True, 'data': ''}


@login_required
def get_points(req, **kwargs):
    """
    :kwargs: 
    """
    amount = points_to_amount(req.user.points)
    return {'status': True, 'data': {'points':req.user.points,'amount':amount}}


def read(req, **kwargs):
    """
    :kwargs: resource, id, data_def
    """
    try:

        resource = DataBaseMappings[kwargs['resource']]
        resource = resource.get_by_id(id)
        data_def = kwargs['data_def']  # fields specified by user
        data = get_data(resource, data_def)

    except Exception as e:
        return {'status': False, 'data': repr(e)}

    return {'status': True, 'data': data}


def read_many(req, **kwargs):
    """
    :kwargs: resource, data_def, filters
    """
    try:

        resource = DataBaseMappings[kwargs['resource']]
        data_def = kwargs['data_def']  # fields specified by user
        filters = kwargs['filters']  # query filters
        resources = resource.get(**filters)
        data = [get_data(resource, data_def) for resource in resources]  # slow

    except Exception as e:
        return {'status': False, 'data': repr(e)}

    return {'status': True, 'data': data}


@login_required
def create(req, **kwargs):
    """
    :kwargs: resource, data
    """
    try:

        resource = DataBaseMappings[kwargs['resource']]
        resource.create(**kwargs['data'])

    except Exception as e:
        return {'status': False, 'data': repr(e)}

    return {'status': True, 'data': ''}


@login_required
def update(req, **kwargs):
    """
    :kwargs: resource, id, data
    """
    try:

        resource = DataBaseMappings[kwargs['resource']]
        data = resource.update(**kwargs['data']).execute()

    except Exception as e:
        return {'status': False, 'data': repr(e)}

    return {'status': True, 'data': data}


@login_required
def delete(req, **kwargs):
    """
    :kwargs: resource, id
    """
    try:

        resource = DataBaseMappings[kwargs['resource']]
        data = resource.delete().where(id=kwargs['id']).execute()

    except Exception as e:
        return {'status': False, 'data': repr(e)}

    return {'status': True, 'data': data}


def get_entries(req, **kwargs):
    """
    :kwargs: level
    """
    thirty_min_ago = datetime.datetime.now() - datetime.timedelta(seconds=30 * 60)
    entries = Entry.select(Entry.entry, Entry.id).where( ((Entry.utime < thirty_min_ago) | (Entry.is_locked == False)) & (Entry.is_translated == False) & (Entry.level==kwargs['level']))

    entries = entries.dicts()[:BATCH]
    for entry in entries:
        Entry.update(utime=datetime.datetime.now(), is_locked=True).where(Entry.id==entry['id']).execute()
    # lock all selected entries

    return {'status':True, 'data':entries}


def get_translations(req, **kwargs):
    """
    :kwargs: level
    """
    if req.user:
        user = req.user
    else:
        user = User.get_by_id(1)
    transes = Translation.select(Entry.id.alias('eid'), Entry.entry, Translation.translation, Translation.id).join(Entry).where( (Translation.passed+Translation.failed < 10) & (Entry.level==kwargs['level']) & (Translation.user != user) )
    

    # first look for translations with less validations
    if BATCH > transes.count(): # translations not up to size BATCH
        diff = BATCH - transes.count() # we want translations of size BATCH
        transes = transes.order_by(Translation.passed.asc(),Translation.failed.asc()).dicts()[:]
        transes2 = Translation.select(Entry.id.alias('eid'), Entry.entry, Translation.translation, Translation.id).join(Entry).where( (Translation.passed+Translation.failed >= 10) & (Entry.level==kwargs['level']) & (Translation.user != user) )
        transes2 = transes2.order_by(Translation.passed.asc(),Translation.failed.asc()).dicts()[:diff]
        transes.extend(transes2)
        return {'status':True, 'data':transes}
    else:
        transes = transes.order_by(Translation.passed.asc(),Translation.failed.asc()).dicts()[:BATCH] # select 10 less translated
        return {'status':True, 'data':transes}



# @login_required
def set_entries(req, **kwargs):
    """
    :kwargs: file
    """

    data = DataURI(kwargs['file'])
    file = BytesIO(data.data)
    if data.mimetype != 'text/csv':
        return {'status':False, 'data':'Accepts CSV.'}
    else:
        df = pd.read_csv(file)
        try:
            tups = list(zip(df.entry, df.level))
            with db.atomic():
                Entry.insert_many(tups, fields=[Entry.entry, Entry.level]).execute()
        except Exception as e:
            return {'status':False, 'data':repr(e)}

    return {'status':True,'data':''}


def set_translations(req, **kwargs):
    """
    :kwargs: trans
    """
    for trans in kwargs['trans']:
        with db.atomic():
            try:
                if req.user:
                    user = req.user
                else:
                    user = User.get_by_id(1)
                entry = Entry.get_by_id(trans['id'])
                Translation.create(entry=entry, translation=trans['trans'], user=user)
                Entry.update(is_locked=False).where(Entry.id==trans['id']).execute()
                Entry.update(is_translated=True).where(Entry.id==trans['id']).execute()

                tcount = user.user_trans.count()
                if (tcount >= 250) and (tcount() <= 500):
                    if user.level != 2:
                        User.update(level = 2).where(User.id==user.id).execute()
                elif (tcount >= 500) and (tcount <= 750):
                    if user.level != 3:
                        User.update(level = 3).where(User.id==user.id).execute()
                elif tcount > 750:
                    if user.level !=4:
                        User.update(level = 4).where(User.id==user.id).execute()
                
            except Exception as e:
                return {'status':False, 'data':repr(e)}
    return {'status':True,'data':'Translation Success.'}
    

def set_validations(req, **kwargs):
    """
    :kwargs: valids
    """
    level = int(kwargs['level'])
    for valids in kwargs['valids']:
        with db.atomic():
            try:
                if req.user:
                    user = req.user
                else:
                    user = User.get_by_id(1)
                translation = Translation.get_by_id(valids['id'])
                Validation.create(rating=valids['rating'], translation=translation, user=user)
                if valids['rating'] > 50:
                    points = round(((100 - valids['rating'])/50)*5)
                    Translation.update(passed=Translation.passed + 1).where(Translation.id==valids['id']).execute()
                    User.update(points= User.points + level*points).where(User.id==translation.user.id).execute()
                else:
                    Translation.update(failed=Translation.failed + 1).where(Translation.id==valids['id']).execute()
                    User.update(points= User.points - level ).where(User.id==translation.user.id).execute()
                User.update(points= User.points + (level*5)).where(User.id==user.id).execute()
            except Exception as e:
                return {'status':False, 'data':repr(e)}
    return {'status':True,'data':'Validations Success.'}


def get_progress(req, **kwargs):
    """
    :kwargs: email
    """
    if req.user:
        user = req.user
    else:
        user = User.get_by_id(1)

    trans = Translation.select().join(User).where(User.id==user.id).order_by(Translation.id.desc())[:10]
    valids= Validation.select().join(User).where(User.id==user.id).order_by(Validation.id.desc())[:10]

    t = []
    for tran in trans:
        t.append({
            'trans':tran.translation,
            'entry':tran.entry.entry,
            'p':tran.passed,
            'f':tran.failed,
        })
    
    v = []
    for val in valids:
        v.append({
            'rating':val.rating,
            'trans':val.translation.translation,
            'entry':val.translation.entry.entry,
            'p':val.translation.passed,
            'f':val.translation.failed,
        })

    data = {
        'transc':user.user_trans.count(),
        'validsc':user.user_valids.count(),
        'trans': t,
        'valids': v,
        'level':user.level,
        'points':user.points,
    }

    return {'status':True, 'data': data}

    
def all_entries(req, **kwargs):
    """
    :kwargs: block, block_size
    """
    
    try:
        end = kwargs['block']*kwargs['block_size']
        start = end - kwargs['block_size']
        entries = Entry.select(Entry.id, Entry.level, Entry.is_locked, Entry.is_translated)
        count = entries.count()
        return {'status':True, 'data':{'entries':entries.dicts()[start:end],'count':count}}
    except Exception as e:
        return {'status':False, 'data':repr(e)}


def all_translations(req, **kwargs):
    """
    :kwargs: block, block_size
    """
    
    try:
        end = kwargs['block']*kwargs['block_size']
        start = end - kwargs['block_size']
        translations = Translation.select()
        count = translations.count()
        trans = []

        for translate in translations[start:end]:
            trans.append({
                'trans':translate.translation,
                'entry':translate.entry.entry,
                'yes':translate.passed,
                'no':translate.failed,
            })
        return {'status':True, 'data':{'trans':trans,'count':count}}
    except Exception as e:
        return {'status':False, 'data':repr(e)}


def all_validations(req, **kwargs):
    """
    :kwargs: block, block_size
    """
    
    try:
        end = kwargs['block']*kwargs['block_size']
        start = end - kwargs['block_size']
        validations = Validation.select()
        count = validations.count()
        valids = []

        for validate in validations[start:end]:
            valids.append({
                'entry': validate.translation.entry.entry,
                'rating':validate.rating,
                'trans':validate.translation.translation,
            })
        return {'status':True, 'data':{'valids':valids,'count':count}}
    except Exception as e:
        return {'status':False, 'data':repr(e)}


actions = {
    "create": create,
    "read": read,
    "update": update,
    "delete": delete,
    "login": login,
    "register": register,
    "redeem_points": redeem_points,
    "generate_pin": generate_pin,
    "get_entries": get_entries,
    "get_translations": get_translations,
    "set_translations": set_translations,
    "set_validations": set_validations,
    "set_entries": set_entries,
    "get_progress": get_progress,
    'all_entries':all_entries,
    "all_translations":all_translations,
    "all_validations":all_validations,
    "get_points":get_points
}
