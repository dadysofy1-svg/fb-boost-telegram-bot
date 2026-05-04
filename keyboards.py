from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states import AdObjectives


# ==================== القائمة الرئيسية ====================

def main_menu(gate_names: dict, subscribed: bool, support_url: str = 'https://t.me/') -> InlineKeyboardMarkup:
    rows = []
    if subscribed:
        gate_buttons = {
            'standard_ad': '🟢 إعلان رابط بوست',
            'dark_post':   '🔵 إعلان دارك بوست',
            'partner_ship':'🟣 إعلان بارتنر شيب',
        }
        keys = [(k, gate_buttons.get(k, v)) for k, v in gate_names.items()]
        for i in range(0, len(keys), 1):
            k, v = keys[i]
            rows.append([InlineKeyboardButton(text=v, callback_data=f'gate:{k}')])
        rows.append([
            InlineKeyboardButton(text='📊 إحصائياتي', callback_data='my_stats'),
        ])
    else:
        rows.append([
            InlineKeyboardButton(text='🔒 غير مشترك — فعّل كودك أولاً', callback_data='redeem')
        ])
    rows.append([
        InlineKeyboardButton(text='🎟️ تفعيل كود Redeem', callback_data='redeem'),
        InlineKeyboardButton(text='🛟 الدعم', url=support_url),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ==================== البروكسي ====================

def proxy_selection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🤖 اختيار تلقائي من القائمة', callback_data='proxy:auto')],
        [InlineKeyboardButton(text='✏️  إدخال بروكسي يدوي',        callback_data='proxy:custom')],
        [InlineKeyboardButton(text='⏭️  تخطي — بدون بروكسي',       callback_data='proxy:skip')],
        [InlineKeyboardButton(text='🏠 القائمة الرئيسية',           callback_data='home')],
    ])


def back_to_proxy() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 تغيير البروكسي', callback_data='proxy:back')],
        [InlineKeyboardButton(text='🏠 القائمة الرئيسية', callback_data='home')],
    ])


# ==================== الأهداف ====================

def objective_selection_keyboard() -> InlineKeyboardMarkup:
    icons = {
        'CONVERSATIONS':      '💬',
        'MESSAGES_MESSENGER': '📨',
        'MESSAGES_WHATSAPP':  '📱',
        'LINK_CLICKS':        '🔗',
        'POST_ENGAGEMENT':    '📈',
        'VIDEO_VIEWS':        '🎬',
    }
    rows = []
    objs = AdObjectives.all()
    for i in range(0, len(objs), 2):
        row = []
        for obj in objs[i:i+2]:
            icon = icons.get(obj, '🎯')
            name = AdObjectives.get_display_name(obj).split('(')[0].strip()
            row.append(InlineKeyboardButton(text=f'{icon} {name}', callback_data=f'objective:{obj}'))
        rows.append(row)
    rows.append([InlineKeyboardButton(text='🏠 القائمة الرئيسية', callback_data='home')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ==================== تأكيد ====================

def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='✅ تأكيد وتشغيل', callback_data='confirm:yes'),
            InlineKeyboardButton(text='❌ إلغاء',         callback_data='confirm:no'),
        ],
        [InlineKeyboardButton(text='🏠 القائمة الرئيسية', callback_data='home')],
    ])


def activate_or_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🟢 نشر نشط',          callback_data='activate:run')],
        [InlineKeyboardButton(text='⏸ نشر ثم إيقاف',     callback_data='activate:run_pause')],
        [InlineKeyboardButton(text='🔙 العودة للقائمة',   callback_data='home')],
    ])


def post_selection_keyboard(posts: list) -> InlineKeyboardMarkup:
    """لوحة اختيار البوست من بوستات الصفحة"""
    rows = []
    for post in posts[:8]:
        pid   = post.get('id', '')
        short = post.get('id', '')
        text  = post.get('message') or post.get('story') or ''
        label = text[:45].replace('\n', ' ') if text else f"📄 بوست {short}"
        rows.append([InlineKeyboardButton(text=f"📌 {label}", callback_data=f'post:{pid}')])
    rows.append([InlineKeyboardButton(text='✏️ إدخال رابط/ID يدوي', callback_data='post:manual')])
    rows.append([InlineKeyboardButton(text='🏠 القائمة الرئيسية',   callback_data='home')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ==================== الصورة ====================

def image_received_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🔄 تغيير الصورة', callback_data='image:change'),
            InlineKeyboardButton(text='⏭️ تخطي الصورة',  callback_data='image:skip'),
        ],
        [InlineKeyboardButton(text='🏠 إلغاء', callback_data='home')],
    ])


# ==================== تنقل عام ====================

def back_home() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🏠 القائمة الرئيسية', callback_data='home')],
    ])


def back_admin() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 لوحة التحكم', callback_data='admin:panel')],
    ])


# ==================== لوحة تحكم الأدمن ====================

def admin_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🎟️ توليد كود Redeem', callback_data='admin:gen_code'),
            InlineKeyboardButton(text='📊 الإحصائيات',        callback_data='admin:stats'),
        ],
        [
            InlineKeyboardButton(text='👤 إضافة/تمديد مشترك', callback_data='admin:set_user'),
            InlineKeyboardButton(text='🗑️  حذف مشترك',         callback_data='admin:remove_user'),
        ],
        [
            InlineKeyboardButton(text='📋 قائمة المشتركين',   callback_data='admin:list_users'),
            InlineKeyboardButton(text='🎟️ عرض الأكواد',        callback_data='admin:list_codes'),
        ],
        [
            InlineKeyboardButton(text='🌐 إضافة بروكسيات',    callback_data='admin:add_proxies'),
            InlineKeyboardButton(text='🗂️  عرض البروكسيات',    callback_data='admin:list_proxies'),
        ],
        [
            InlineKeyboardButton(text='📢 رسالة جماعية',      callback_data='admin:broadcast'),
            InlineKeyboardButton(text='⚙️  إعدادات البوت',     callback_data='admin:settings'),
        ],
        [InlineKeyboardButton(text='🏠 خروج من لوحة التحكم', callback_data='home')],
    ])


def admin_users_keyboard(users: list) -> InlineKeyboardMarkup:
    rows = []
    for u in users[:8]:
        uid = u['user_id']
        name = u['custom_name'] or u['first_name'] or f'user_{uid}'
        sub = '🟢' if u['subscription_until'] else '🔴'
        rows.append([InlineKeyboardButton(
            text=f'{sub} {name} ({uid})',
            callback_data=f'admin:user_info:{uid}'
        )])
    rows.append([InlineKeyboardButton(text='🔙 لوحة التحكم', callback_data='admin:panel')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def user_action_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='➕ تمديد اشتراك',     callback_data=f'admin:extend:{user_id}'),
            InlineKeyboardButton(text='🗑️ حذف',               callback_data=f'admin:del:{user_id}'),
        ],
        [InlineKeyboardButton(text='🔙 قائمة المشتركين',    callback_data='admin:list_users')],
    ])


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✏️  تغيير اسم البوت',    callback_data='admin:set_botname')],
        [InlineKeyboardButton(text='🔗 تغيير رابط الدعم',   callback_data='admin:set_support')],
        [InlineKeyboardButton(text='🔙 لوحة التحكم',         callback_data='admin:panel')],
    ])
