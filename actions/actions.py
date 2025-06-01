from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import logging

logger = logging.getLogger(__name__)

# المدن المغربية المدعومة
MOROCCAN_CITIES = [
    'الرباط', 'الدار البيضاء', 'الدارالبيضاء', 'مراكش', 'فاس', 
    'أكادير', 'طنجة', 'وجدة', 'تطوان', 'الحسيمة', 'القنيطرة', 'سلا'
]

# الوجهات الدولية المدعومة
INTERNATIONAL_DESTINATIONS = [
    "باريس", "لندن", "مدريد", "دبي", "القاهرة", "تونس",
    "إسطنبول", "روما", "برلين", "أمستردام", "بروكسل", "نيويورك",
    "تورنتو", "مونتريال", "جنيف", "زيوريخ"
]

class ValidateFlightForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_flight_form"

    def validate_ville_depart(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        logger.info(f"Validating ville_depart: slot_value={slot_value}")
        
        # استخراج اسم المدينة من entities
        city = None
        entities = tracker.latest_message.get('entities', [])
        
        logger.info(f"Available entities: {entities}")
        
        # البحث عن أي entity يحتوي على مدينة مغربية
        for entity in entities:
            entity_value = entity.get('value', '')
            entity_type = entity.get('entity', '')
            logger.info(f"Checking entity: {entity_value} (type: {entity_type})")
            
            if any(moroccan_city in entity_value for moroccan_city in MOROCCAN_CITIES):
                city = entity_value
                logger.info(f"Found Moroccan city in entity: {city}")
                break
        
        # إذا لم نجد في entities، نستخدم slot_value
        if not city and slot_value:
            city = slot_value
            logger.info(f"Using slot_value as city: {city}")
            
        if city and any(moroccan_city in city for moroccan_city in MOROCCAN_CITIES):
            logger.info(f"Valid departure city detected: {city}")
            return {"ville_depart": city}
        else:
            dispatcher.utter_message(
                text="عذراً، يرجى اختيار مدينة مغربية صحيحة للمغادرة.\n"
                     "المدن المتاحة: الرباط، الدار البيضاء، مراكش، فاس، أكادير، طنجة"
            )
            return {"ville_depart": None}

    def validate_ville_destination(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        logger.info(f"Validating ville_destination: slot_value={slot_value}")
        
        # استخراج اسم المدينة من entities
        city = None
        entities = tracker.latest_message.get('entities', [])
        
        for entity in entities:
            entity_value = entity.get('value', '')
            # البحث في الوجهات الدولية أو المدن المغربية (للرحلات الداخلية)
            if (any(dest in entity_value for dest in INTERNATIONAL_DESTINATIONS) or
                any(moroccan_city in entity_value for moroccan_city in MOROCCAN_CITIES)):
                city = entity_value
                logger.info(f"Found destination city in entity: {city}")
                break
                
        if not city and slot_value:
            city = slot_value
            
        if city:
            logger.info(f"Valid destination city detected: {city}")
            return {"ville_destination": city}
        else:
            dispatcher.utter_message(
                text="يرجى تحديد مدينة الوجهة.\n"
                     "الوجهات المتاحة: باريس، لندن، مدريد، دبي، القاهرة، تونس، إسطنبول، وغيرها"
            )
            return {"ville_destination": None}

    def validate_date_depart(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value:
            logger.info(f"Valid departure date: {slot_value}")
            return {"date_depart": slot_value}
        else:
            dispatcher.utter_message(text="متى تريد السفر؟ مثال: 15 مايو، غداً، الأسبوع القادم")
            return {"date_depart": None}

    def validate_classe(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        if slot_value:
            slot_value_clean = slot_value.strip().lower()
            
            # تنظيف وتوحيد الإجابات
            if any(classe in slot_value_clean for classe in ["اقتصادية", "عادية", "عاديه", "economy", "eco"]):
                logger.info("Selected economy class")
                return {"classe": "اقتصادية"}
            elif any(classe in slot_value_clean for classe in ["أعمال", "بزنس", "business"]):
                logger.info("Selected business class")
                return {"classe": "أعمال"}
            elif any(classe in slot_value_clean for classe in ["أولى", "فاخرة", "first", "فيرست"]):
                logger.info("Selected first class")
                return {"classe": "أولى"}
            else:
                dispatcher.utter_message(text="الدرجات المتاحة: اقتصادية، أعمال، أولى")
                return {"classe": None}
        else:
            dispatcher.utter_message(text="أي درجة تفضل؟ (اقتصادية، أعمال، أولى)")
            return {"classe": None}

class ValidateHotelForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_hotel_form"

    def validate_ville_hotel(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        logger.info(f"Validating ville_hotel: slot_value={slot_value}")
        
        # استخراج اسم المدينة من entities
        city = None
        entities = tracker.latest_message.get('entities', [])
        
        for entity in entities:
            entity_value = entity.get('value', '')
            if any(moroccan_city in entity_value for moroccan_city in MOROCCAN_CITIES):
                city = entity_value
                logger.info(f"Found hotel city in entity: {city}")
                break
                
        if not city and slot_value:
            city = slot_value
            
        if city and any(moroccan_city in city for moroccan_city in MOROCCAN_CITIES):
            logger.info(f"Valid hotel city detected: {city}")
            return {"ville_hotel": city}
        else:
            dispatcher.utter_message(
                text="عذراً، يرجى اختيار مدينة صحيحة للإقامة.\n"
                     "المدن المتاحة: الرباط، الدار البيضاء، مراكش، فاس، أكادير، طنجة"
            )
            return {"ville_hotel": None}

    def validate_categorie_hotel(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        if slot_value:
            slot_value_clean = slot_value.strip()
            
            # تنظيف الإجابة وتوحيدها
            if "3" in slot_value_clean or "ثلاث" in slot_value_clean:
                logger.info("Selected 3-star hotel")
                return {"categorie_hotel": "3 نجوم"}
            elif "4" in slot_value_clean or "أربع" in slot_value_clean:
                logger.info("Selected 4-star hotel")
                return {"categorie_hotel": "4 نجوم"}
            elif "5" in slot_value_clean or "خمس" in slot_value_clean:
                logger.info("Selected 5-star hotel")
                return {"categorie_hotel": "5 نجوم"}
            elif "فاخر" in slot_value_clean or "luxury" in slot_value_clean.lower():
                logger.info("Selected luxury hotel")
                return {"categorie_hotel": "فاخر"}
            else:
                dispatcher.utter_message(text="الفئات المتاحة: 3 نجوم، 4 نجوم، 5 نجوم، فاخر")
                return {"categorie_hotel": None}
        else:
            dispatcher.utter_message(text="كم نجمة تريد للفندق؟ (3، 4، 5 نجوم)")
            return {"categorie_hotel": None}
            
    def validate_nombre_personnes(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        if slot_value:
            logger.info(f"Valid number of persons: {slot_value}")
            return {"nombre_personnes": slot_value}
        else:
            dispatcher.utter_message(text="كم عدد الأشخاص؟ مثال: شخصين، 4 أشخاص")
            return {"nombre_personnes": None}

class ActionSearchFlights(Action):
    def name(self) -> Text:
        return "action_search_flights"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ville_depart = tracker.get_slot("ville_depart")
        ville_destination = tracker.get_slot("ville_destination")
        date_depart = tracker.get_slot("date_depart")
        classe = tracker.get_slot("classe")
        
        logger.info(f"Flight search: {ville_depart} -> {ville_destination} on {date_depart} ({classe})")
        
        # التأكد من وجود المعلومات الأساسية
        if not ville_depart or not ville_destination:
            dispatcher.utter_message(text="عذراً، أحتاج إلى معرفة مدينة المغادرة والوجهة أولاً.")
            return []
        
        # بناء رسالة النتائج
        message = f"🛫 تم العثور على رحلات من {ville_depart} إلى {ville_destination}\n"
        
        if date_depart:
            message += f"📅 تاريخ السفر: {date_depart}\n"
        if classe:
            message += f"💺 الدرجة: {classe}\n"
            
        message += "\n" + "="*40 + "\n\n"
        
        # خيارات الرحلات (محاكاة)
        message += "✈️ **الخيار الأول: الخطوط الملكية المغربية**\n"
        message += "   🕐 المغادرة: 08:30 - الوصول: 12:45\n"
        message += "   💰 السعر: 3,500 درهم\n"
        message += "   ⭐ التقييم: 4.2/5\n"
        message += "   🎯 المميزات: وجبة مجانية، أمتعة 23 كغ\n\n"
        
        message += "✈️ **الخيار الثاني: العربية للطيران**\n"
        message += "   🕐 المغادرة: 14:20 - الوصول: 18:35\n"
        message += "   💰 السعر: 2,800 درهم\n"
        message += "   ⭐ التقييم: 4.0/5\n"
        message += "   🎯 المميزات: سعر اقتصادي، أمتعة يد فقط\n\n"
        
        message += "🔹 أي خيار تفضل؟ قل **'الخيار الأول'** أو **'الخيار الثاني'**"
        
        dispatcher.utter_message(text=message)
        return []

class ActionSearchHotels(Action):
    def name(self) -> Text:
        return "action_search_hotels"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ville_hotel = tracker.get_slot("ville_hotel")
        categorie_hotel = tracker.get_slot("categorie_hotel") 
        nombre_personnes = tracker.get_slot("nombre_personnes")
        quartier = tracker.get_slot("quartier")
        
        logger.info(f"Hotel search: {ville_hotel}, {categorie_hotel}, {nombre_personnes} persons")
        
        # التأكد من وجود المعلومات الأساسية
        if not ville_hotel:
            dispatcher.utter_message(text="أحتاج إلى معرفة المدينة أولاً. في أي مدينة تريد الإقامة؟")
            return []
            
        if not categorie_hotel:
            dispatcher.utter_message(text="أحتاج إلى معرفة فئة الفندق. كم نجمة تريد؟ (3، 4، 5 نجوم)")
            return []
            
        if not nombre_personnes:
            dispatcher.utter_message(text="أحتاج إلى معرفة عدد الأشخاص. كم شخص؟")
            return []
        
        # إنشاء رسالة البحث
        message = f"🏨 تم العثور على فنادق مميزة في {ville_hotel}\n"
        message += f"⭐ الفئة: {categorie_hotel}\n"
        message += f"👥 عدد الأشخاص: {nombre_personnes}\n"
        
        if quartier:
            message += f"📍 المنطقة المفضلة: {quartier}\n"
            
        message += "\n" + "="*40 + "\n\n"
        
        # عرض الخيارات بناءً على المدينة والفئة
        if "مراكش" in ville_hotel:
            message += "🏨 **الخيار الأول: فندق المامونية الشهير**\n"
            message += "   💰 السعر: 1,200 درهم/ليلة\n"
            message += "   ⭐ التقييم: 4.8/5\n"
            message += "   🎯 المميزات: سبا فاخر، 3 مطاعم، حدائق تاريخية\n"
            message += "   📍 الموقع: وسط المدينة القديمة\n\n"
            
            message += "🏨 **الخيار الثاني: فندق أطلس مراكش**\n"
            message += "   💰 السعر: 850 درهم/ليلة\n"
            message += "   ⭐ التقييم: 4.5/5\n"
            message += "   🎯 المميزات: مسبح، إفطار مجاني، واي فاي\n"
            message += "   📍 الموقع: المدينة الجديدة\n\n"
            
        elif "الرباط" in ville_hotel:
            message += "🏨 **الخيار الأول: فندق تور حسان**\n"
            message += "   💰 السعر: 900 درهم/ليلة\n"
            message += "   ⭐ التقييم: 4.6/5\n"
            message += "   🎯 المميزات: إطلالة على البحر، مطعم راقي\n"
            message += "   📍 الموقع: قرب صومعة حسان\n\n"
            
            message += "🏨 **الخيار الثاني: فندق هيلتون الرباط**\n"
            message += "   💰 السعر: 1,100 درهم/ليلة\n"
            message += "   ⭐ التقييم: 4.7/5\n"
            message += "   🎯 المميزات: مركز أعمال، نادي رياضي\n"
            message += "   📍 الموقع: وسط المدينة\n\n"
            
        else:
            # فنادق عامة للمدن الأخرى
            message += "🏨 **الخيار الأول: فندق الأطلس الكبير**\n"
            message += "   💰 السعر: 800 درهم/ليلة\n"
            message += "   ⭐ التقييم: 4.5/5\n"
            message += "   🎯 المميزات: مسبح، إفطار مجاني، واي فاي\n"
            message += "   📍 الموقع: وسط المدينة\n\n"
            
            message += "🏨 **الخيار الثاني: فندق النخيل الذهبي**\n"
            message += "   💰 السعر: 650 درهم/ليلة\n"
            message += "   ⭐ التقييم: 4.2/5\n"
            message += "   🎯 المميزات: موقع ممتاز، خدمة 24/7\n"
            message += "   📍 الموقع: قرب المعالم السياحية\n\n"
        
        message += "🔹 أي فندق تفضل؟ قل **'الخيار الأول'** أو **'الخيار الثاني'**"
        
        dispatcher.utter_message(text=message)
        return []

class ActionSelectOption(Action):
    def name(self) -> Text:
        return "action_select_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # الحصول على رسالة المستخدم لفهم الخيار المحدد
        user_message = tracker.latest_message.get('text', '').lower()
        
        option_selected = ""
        option_number = ""
        
        # تحديد الخيار المحدد
        if any(word in user_message for word in ['أول', 'الأول', '1', 'رقم 1', 'خيار 1']):
            option_selected = "الخيار الأول"
            option_number = "1"
        elif any(word in user_message for word in ['ثان', 'الثاني', '2', 'رقم 2', 'خيار 2']):
            option_selected = "الخيار الثاني"
            option_number = "2"
        else:
            # إذا لم نتمكن من تحديد الخيار
            dispatcher.utter_message(
                text="لم أتمكن من فهم اختيارك بوضوح.\n"
                     "يرجى قول 'الخيار الأول' أو 'الخيار الثاني'"
            )
            return []
        
        logger.info(f"User selected option: {option_number}")
        
        # تأكيد الاختيار
        message = f"✅ ممتاز! لقد اخترت **{option_selected}**\n\n"
        
        # تحديد نوع الحجز
        is_flight = bool(tracker.get_slot("ville_depart") or tracker.get_slot("ville_destination"))
        is_hotel = bool(tracker.get_slot("ville_hotel"))
        
        if is_flight:
            if option_number == "1":
                message += "🛫 رحلة الخطوط الملكية المغربية\n"
                message += "💰 السعر: 3,500 درهم\n"
            else:
                message += "🛫 رحلة العربية للطيران\n"
                message += "💰 السعر: 2,800 درهم\n"
                
        elif is_hotel:
            ville_hotel = tracker.get_slot("ville_hotel")
            if "مراكش" in str(ville_hotel):
                if option_number == "1":
                    message += "🏨 فندق المامونية الشهير\n"
                    message += "💰 السعر: 1,200 درهم/ليلة\n"
                else:
                    message += "🏨 فندق أطلس مراكش\n"
                    message += "💰 السعر: 850 درهم/ليلة\n"
            else:
                if option_number == "1":
                    message += "🏨 الفندق الأول المحدد\n"
                    message += "💰 سعر مناسب\n"
                else:
                    message += "🏨 الفندق الثاني المحدد\n"
                    message += "💰 سعر اقتصادي\n"
        
        message += "\n🤝 هل تريد المتابعة مع هذا الاختيار؟\n"
        message += "• قل **'نعم'** أو **'أؤكد'** للمتابعة\n"
        message += "• قل **'لا'** أو **'غير'** للتغيير"
        
        dispatcher.utter_message(text=message)
        
        # حفظ الخيار المحدد
        return [{"event": "slot", "name": "selected_option", "value": option_number}]

class ActionConfirmReservation(Action):
    def name(self) -> Text:
        return "action_confirm_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # التحقق من وجود خيار محدد
        selected_option = tracker.get_slot("selected_option")
        
        if not selected_option:
            dispatcher.utter_message(
                text="يبدو أنك تريد التأكيد، لكن لم تختر خياراً بعد.\n"
                     "دعني أكمل مساعدتك في الحجز أولاً!"
            )
            return []
        
        # تحديد نوع الحجز
        is_flight_booking = bool(tracker.get_slot("ville_depart") or tracker.get_slot("ville_destination"))
        is_hotel_booking = bool(tracker.get_slot("ville_hotel"))
        
        # جمع تفاصيل الحجز
        ville_depart = tracker.get_slot("ville_depart")
        ville_destination = tracker.get_slot("ville_destination")
        date_depart = tracker.get_slot("date_depart")
        classe = tracker.get_slot("classe")
        ville_hotel = tracker.get_slot("ville_hotel")
        categorie_hotel = tracker.get_slot("categorie_hotel")
        nombre_personnes = tracker.get_slot("nombre_personnes")
        
        logger.info(f"Confirming reservation - Option: {selected_option}, Flight: {is_flight_booking}, Hotel: {is_hotel_booking}")
        
        # بناء رسالة التأكيد
        message = "🎉 **تهانينا! تم تأكيد حجزك بنجاح!** 🎉\n\n"
        message += "="*50 + "\n"
        message += "📋 **تفاصيل حجزك:**\n"
        message += "="*50 + "\n\n"
        
        # تفاصيل رحلة الطيران
        if is_flight_booking and ville_depart and ville_destination:
            message += "✈️ **رحلة الطيران:**\n"
            message += f"   📍 من: {ville_depart}\n"
            message += f"   📍 إلى: {ville_destination}\n"
            
            if date_depart:
                message += f"   📅 تاريخ السفر: {date_depart}\n"
            if classe:
                message += f"   💺 الدرجة: {classe}\n"
                
            if selected_option == "1":
                message += "   🛫 الناقل: الخطوط الملكية المغربية\n"
                message += "   💰 السعر: 3,500 درهم\n"
                message += "   🕐 التوقيت: 08:30 - 12:45\n"
            elif selected_option == "2":
                message += "   🛫 الناقل: العربية للطيران\n"
                message += "   💰 السعر: 2,800 درهم\n"
                message += "   🕐 التوقيت: 14:20 - 18:35\n"
                
            message += "\n"
        
        # تفاصيل الفندق
        if is_hotel_booking and ville_hotel:
            message += "🏨 **حجز الفندق:**\n"
            message += f"   📍 المدينة: {ville_hotel}\n"
            
            if categorie_hotel:
                message += f"   ⭐ الفئة: {categorie_hotel}\n"
            if nombre_personnes:
                message += f"   👥 عدد الأشخاص: {nombre_personnes}\n"
                
            if "مراكش" in ville_hotel:
                if selected_option == "1":
                    message += "   🏨 الفندق: فندق المامونية الشهير\n"
                    message += "   💰 السعر: 1,200 درهم/ليلة\n"
                elif selected_option == "2":
                    message += "   🏨 الفندق: فندق أطلس مراكش\n"
                    message += "   💰 السعر: 850 درهم/ليلة\n"
            elif "الرباط" in ville_hotel:
                if selected_option == "1":
                    message += "   🏨 الفندق: فندق تور حسان\n"
                    message += "   💰 السعر: 900 درهم/ليلة\n"
                elif selected_option == "2":
                    message += "   🏨 الفندق: فندق هيلتون الرباط\n"
                    message += "   💰 السعر: 1,100 درهم/ليلة\n"
            else:
                if selected_option == "1":
                    message += "   🏨 الفندق: فندق الأطلس الكبير\n"
                    message += "   💰 السعر: 800 درهم/ليلة\n"
                elif selected_option == "2":
                    message += "   🏨 الفندق: فندق النخيل الذهبي\n"
                    message += "   💰 السعر: 650 درهم/ليلة\n"
                    
            message += "\n"
        
        # معلومات إضافية
        message += "="*50 + "\n"
        message += "📧 **ستصلك تفاصيل الحجز عبر البريد الإلكتروني خلال 10 دقائق**\n\n"
        message += "📱 **خدمة العملاء:**\n"
        message += "   📞 الهاتف: +212-5XX-XXXXXX\n"
        message += "   💬 واتساب: +212-6XX-XXXXXX\n"
        message += "   ⏰ متاح 24/7\n\n"
        message += "🎯 **نصائح مهمة:**\n"
        message += "   • احتفظ برقم الحجز للمراجعة\n"
        message += "   • تأكد من صحة جواز السفر (للطيران الدولي)\n"
        message += "   • اوصل للمطار قبل 3 ساعات (دولي) أو 2 ساعة (محلي)\n"
        message += "   • تحقق من شروط الإلغاء والتعديل\n\n"
        message += "🔄 **لحجز جديد، قل 'مرحبا' أو اضغط إعادة التشغيل**\n\n"
        message += "🌟 **شكراً لثقتك بوكالة السفر الذكية!**\n"
        message += "✈️🏨 نتمنى لك رحلة سعيدة وإقامة ممتعة! ✨"
        
        dispatcher.utter_message(text=message)
        
        # مسح البيانات بعد التأكيد للاستعداد لحجز جديد
        return [
            {"event": "slot", "name": "selected_option", "value": None},
            {"event": "slot", "name": "ville_depart", "value": None},
            {"event": "slot", "name": "ville_destination", "value": None},
            {"event": "slot", "name": "date_depart", "value": None},
            {"event": "slot", "name": "classe", "value": None},
            {"event": "slot", "name": "ville_hotel", "value": None},
            {"event": "slot", "name": "categorie_hotel", "value": None},
            {"event": "slot", "name": "nombre_personnes", "value": None}
        ]

class ActionChangeOption(Action):
    def name(self) -> Text:
        return "action_change_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # التحقق من نوع الحجز الحالي
        is_flight = bool(tracker.get_slot("ville_depart") or tracker.get_slot("ville_destination"))
        is_hotel = bool(tracker.get_slot("ville_hotel"))
        
        message = "🔄 **لا مشكلة! يمكنك تغيير أي شيء تريده**\n\n"
        
        if is_flight:
            message += "✈️ **للرحلات الجوية، يمكنك تغيير:**\n"
            message += "   📍 مدينة المغادرة - قل 'غير المغادرة'\n"
            message += "   📍 مدينة الوجهة - قل 'غير الوجهة'\n"
            message += "   📅 تاريخ السفر - قل 'غير التاريخ'\n"
            message += "   💺 درجة السفر - قل 'غير الدرجة'\n\n"
            
        if is_hotel:
            message += "🏨 **للفنادق، يمكنك تغيير:**\n"
            message += "   📍 المدينة - قل 'غير المدينة'\n"
            message += "   ⭐ فئة الفندق - قل 'غير الفئة'\n"
            message += "   👥 عدد الأشخاص - قل 'غير العدد'\n\n"
            
        if not is_flight and not is_hotel:
            message += "🎯 **يمكنك بدء حجز جديد:**\n"
            message += "   ✈️ قل 'أريد حجز رحلة طيران'\n"
            message += "   🏨 قل 'أريد حجز فندق'\n\n"
            
        message += "💡 **أو أخبرني مباشرة بما تريد تعديله**"
        
        dispatcher.utter_message(text=message)
        
        # مسح الخيار المحدد لإعطاء المستخدم فرصة جديدة
        return [{"event": "slot", "name": "selected_option", "value": None}]

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # التحقق من السياق الحالي
        active_form = tracker.active_loop.get('name') if tracker.active_loop else None
        requested_slot = tracker.get_slot('requested_slot')
        
        if active_form == 'flight_form':
            if requested_slot == 'ville_depart':
                message = "🤔 لم أفهم المدينة. من أي مدينة تريد السفر؟\n"
                message += "المدن المتاحة: الرباط، الدار البيضاء، مراكش، فاس، أكادير، طنجة"
            elif requested_slot == 'ville_destination':
                message = "🤔 لم أفهم الوجهة. إلى أي مدينة تريد السفر؟\n"
                message += "مثال: باريس، لندن، مدريد، دبي"
            elif requested_slot == 'date_depart':
                message = "🤔 لم أفهم التاريخ. متى تريد السفر؟\n"
                message += "مثال: 15 مايو، غداً، الأسبوع القادم"
            elif requested_slot == 'classe':
                message = "🤔 لم أفهم الدرجة. أي درجة تفضل؟\n"
                message += "الخيارات: اقتصادية، أعمال، أولى"
            else:
                message = "🤔 لم أفهم ردك. يمكنك المساعدة في حجز رحلة طيران."
                
        elif active_form == 'hotel_form':
            if requested_slot == 'ville_hotel':
                message = "🤔 لم أفهم المدينة. في أي مدينة تريد الإقامة؟\n"
                message += "المدن المتاحة: الرباط، الدار البيضاء، مراكش، فاس، أكادير، طنجة"
            elif requested_slot == 'categorie_hotel':
                message = "🤔 لم أفهم فئة الفندق. كم نجمة تريد؟\n"
                message += "الخيارات: 3 نجوم، 4 نجوم، 5 نجوم"
            elif requested_slot == 'nombre_personnes':
                message = "🤔 لم أفهم العدد. كم عدد الأشخاص؟\n"
                message += "مثال: شخصين، 4 أشخاص"
            else:
                message = "🤔 لم أفهم ردك. يمكنني المساعدة في حجز فندق."
                
        else:
            # رسالة عامة عندما لا نكون في form
            message = "🤔 عذراً، لم أتمكن من فهم طلبك بوضوح.\n\n"
            message += "💡 **يمكنني مساعدتك في:**\n"
            message += "   ✈️ حجز رحلات طيران - قل 'أريد حجز رحلة'\n"
            message += "   🏨 حجز فنادق - قل 'أريد حجز فندق'\n"
            message += "   ❓ الحصول على مساعدة - قل 'مساعدة'\n\n"
            message += "🗣️ **أو اكتب ما تريده بكلمات بسيطة**"
        
        dispatcher.utter_message(text=message)
        return []

class ActionRestart(Action):
    def name(self) -> Text:
        return "action_restart"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(
            text="🔄 تم إعادة تشغيل النظام بنجاح!\n\n"
                 "🌟 مرحباً بك مجدداً في وكالة السفر الذكية!\n\n"
                 "💡 كيف يمكنني مساعدتك اليوم؟\n"
                 "   ✈️ حجز رحلة طيران\n"
                 "   🏨 حجز فندق\n"
                 "   🎯 تخطيط رحلة"
        )
        
        return [{"event": "restart"}]