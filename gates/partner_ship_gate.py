from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from keyboards import (
    back_home, proxy_selection_keyboard, back_to_proxy,
    objective_selection_keyboard, confirm_keyboard, activate_or_back_keyboard
)
from states import AdObjectives, GateConstants, AdGateStates
from gates.base_gate import BaseGate
from services.facebook_api import run_partner_ship_ad, run_partner_ship_ad_then_pause


def _result_text(result: dict, gate_name: str) -> str:
    paused = result.get('paused', False)
    status = "⏸ <b>تم النشر ثم الإيقاف بنجاح!</b>" if paused else "🟢 <b>الإعلان يعمل الآن!</b>"
    return (
        f"✅ <b>تم تشغيل {gate_name} بنجاح!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Campaign ID:</b> <code>{result.get('campaign_id', 'N/A')}</code>\n"
        f"📦 <b>Ad Set ID:</b>  <code>{result.get('ad_set_id', 'N/A')}</code>\n"
        f"🎨 <b>Creative ID:</b> <code>{result.get('creative_id', 'N/A')}</code>\n"
        f"📌 <b>Ad ID:</b>      <code>{result.get('ad_id', 'N/A')}</code>\n\n"
        f"{status}"
    )


class PartnerShipGate(BaseGate):
    def __init__(self):
        super().__init__('partner_ship', '🟣 إعلان بارتنر شيب', 'partner_ship')

    async def enter(self, call: CallbackQuery, state: FSMContext, config: dict):
        await state.update_data(gate_id=self.gate_id, gate_type=self.gate_type, gate_name=self.gate_name)
        await state.set_state(AdGateStates.waiting_proxy)
        await call.message.edit_text(
            f"🚪 <b>{self.gate_name}</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 <b>خطوات العمل:</b>\n"
            "1️⃣ البروكسي\n2️⃣ الكوكيز\n3️⃣ Account ID\n"
            "4️⃣ Ad Set ID\n5️⃣ Ad Code\n"
            "6️⃣ الهدف\n7️⃣ الميزانية والأيام\n8️⃣ مراجعة وتشغيل\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔽 <b>الخطوة 1:</b> اختر البروكسي",
            reply_markup=proxy_selection_keyboard()
        )

    async def handle_proxy_auto(self, call: CallbackQuery, state: FSMContext, proxy: str = None):
        if not proxy:
            await call.answer("⚠️ لا توجد بروكسيات متاحة", show_alert=True)
            return
        await state.update_data(proxy=proxy)
        await state.set_state(AdGateStates.waiting_cookies)
        await call.message.edit_text(
            f"✅ <b>البروكسي:</b> {proxy}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔽 <b>الخطوة 2:</b> أرسل كوكيز فيسبوك",
            reply_markup=back_to_proxy()
        )

    async def handle_proxy_skip(self, call: CallbackQuery, state: FSMContext):
        await state.update_data(proxy=None)
        await state.set_state(AdGateStates.waiting_cookies)
        await call.message.edit_text(
            "✅ <b>تخطي البروكسي</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔽 <b>الخطوة 2:</b> أرسل كوكيز فيسبوك",
            reply_markup=back_to_proxy()
        )

    async def handle_proxy_custom(self, message: Message, state: FSMContext):
        is_valid, error = self.validate_proxy(message.text)
        if not is_valid:
            await message.answer(error, reply_markup=back_home())
            return
        proxy = message.text.strip() if message.text.strip().lower() != 'skip' else None
        await state.update_data(proxy=proxy)
        await state.set_state(AdGateStates.waiting_cookies)
        await message.answer(
            f"✅ <b>البروكسي:</b> {proxy or 'بدون'}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔽 <b>الخطوة 2:</b> أرسل كوكيز فيسبوك",
            reply_markup=back_to_proxy()
        )

    async def handle_proxy_back(self, call: CallbackQuery, state: FSMContext):
        await state.set_state(AdGateStates.waiting_proxy)
        await call.message.edit_text("🔽 <b>اختر البروكسي</b>", reply_markup=proxy_selection_keyboard())

    async def handle_cookies(self, message: Message, state: FSMContext):
        is_valid, error = self.validate_cookies(message.text)
        if not is_valid:
            await message.answer(error, reply_markup=back_home())
            return
        await state.update_data(cookies=message.text.strip())
        await state.set_state(AdGateStates.waiting_ad_account_id)
        await message.answer(
            "✅ <b>تم حفظ الكوكيز</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔽 <b>الخطوة 3:</b> أدخل Ad Account ID",
            reply_markup=back_home()
        )

    async def handle_ad_account_id(self, message: Message, state: FSMContext):
        is_valid, result = self.validate_ad_account_id(message.text)
        if not is_valid:
            await message.answer(result, reply_markup=back_home())
            return
        await state.update_data(ad_account_id=result)
        await state.set_state(AdGateStates.waiting_ad_set_id)
        await message.answer(
            f"✅ <b>Account ID:</b> {result}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔽 <b>الخطوة 4:</b> أدخل Ad Set ID\n"
            "(معرف Ad Set من البارتنر شيب)",
            reply_markup=back_home()
        )

    async def handle_ad_set_id(self, message: Message, state: FSMContext):
        ad_set_id = message.text.strip()
        if not ad_set_id or len(ad_set_id) < 5:
            await message.answer("❌ Ad Set ID غير صحيح", reply_markup=back_home())
            return
        await state.update_data(ad_set_id=ad_set_id)
        await state.set_state(AdGateStates.waiting_post_id)
        await message.answer(
            f"✅ <b>Ad Set ID:</b> {ad_set_id}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔽 <b>الخطوة 5:</b> أدخل Ad Code\n"
            "(كود الإعلان من البارتنر شيب)",
            reply_markup=back_home()
        )

    async def handle_ad_code(self, message: Message, state: FSMContext):
        is_valid, error = self.validate_ad_code(message.text)
        if not is_valid:
            await message.answer(error, reply_markup=back_home())
            return
        await state.update_data(ad_code=message.text.strip())
        await state.set_state(AdGateStates.waiting_objective)
        await message.answer(
            f"✅ <b>Ad Code:</b> {message.text.strip()}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔽 <b>الخطوة 6:</b> اختر هدف الإعلان",
            reply_markup=objective_selection_keyboard()
        )

    async def handle_objective(self, call: CallbackQuery, state: FSMContext):
        objective = call.data.split(':', 1)[1]
        await state.update_data(objective=objective)
        await state.set_state(AdGateStates.waiting_daily_budget)
        await call.message.edit_text(
            f"✅ <b>الهدف:</b> {AdObjectives.get_display_name(objective)}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔽 <b>الخطوة 7:</b> أدخل الميزانية اليومية (USD)\n"
            f"(الافتراضي: {GateConstants.DEFAULT_BUDGET}$)",
            reply_markup=back_home()
        )
        await call.answer()

    async def handle_daily_budget(self, message: Message, state: FSMContext):
        is_valid, result = self.validate_budget(message.text)
        if not is_valid:
            await message.answer(result, reply_markup=back_home())
            return
        await state.update_data(daily_budget=result)
        await state.set_state(AdGateStates.waiting_days)
        await message.answer(
            f"✅ <b>الميزانية:</b> {result}$\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔽 <b>الخطوة 8:</b> أدخل عدد الأيام\n"
            f"(الافتراضي: {GateConstants.DEFAULT_DAYS})",
            reply_markup=back_home()
        )

    async def handle_days(self, message: Message, state: FSMContext):
        is_valid, result = self.validate_days(message.text)
        if not is_valid:
            await message.answer(result, reply_markup=back_home())
            return
        await state.update_data(days=result)
        await state.set_state(AdGateStates.waiting_confirm)
        data = await state.get_data()
        await message.answer(self.format_summary(data), reply_markup=confirm_keyboard())

    async def handle_confirm(self, call: CallbackQuery, state: FSMContext):
        if call.data == 'confirm:yes':
            await state.set_state(AdGateStates.waiting_activate)
            await call.message.edit_text(
                "🚀 <b>جاهز للتشغيل!</b>\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "اختر طريقة النشر:",
                reply_markup=activate_or_back_keyboard()
            )
        else:
            await state.clear()
            await call.message.edit_text("❌ <b>تم الإلغاء</b>", reply_markup=back_home())
        await call.answer()

    async def handle_activate(self, call: CallbackQuery, state: FSMContext):
        data   = await state.get_data()
        action = call.data

        if action not in ('activate:run', 'activate:run_pause'):
            await state.clear()
            await call.message.edit_text("🏠 <b>تم الإلغاء</b>", reply_markup=back_home())
            await call.answer()
            return

        pause = action == 'activate:run_pause'
        label = "⏸ نشر ثم إيقاف" if pause else "🟢 نشر نشط"

        await call.message.edit_text(
            f"⏳ <b>جاري إنشاء إعلان البارتنر شيب... ({label})</b>\n\n"
            "🔗 ربط Ad Code...\nيرجى الانتظار"
        )
        try:
            fn     = run_partner_ship_ad_then_pause if pause else run_partner_ship_ad
            result = await fn(data)
            if result['success']:
                await call.message.edit_text(_result_text(result, self.gate_name), reply_markup=back_home())
            else:
                await call.message.edit_text(
                    f"❌ <b>فشل في خطوة: {result.get('step', '?')}</b>\n\n"
                    f"🔴 {result.get('error', 'خطأ غير معروف')}",
                    reply_markup=back_home()
                )
        except Exception as e:
            await call.message.edit_text(f"❌ <b>خطأ:</b>\n{e}", reply_markup=back_home())
        await call.answer()
