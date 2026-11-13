"""
UZHAVAR AI - Multilingual Agricultural Intent Classifier
Classifies agricultural queries into 14 distinct categories across 10 Indian languages.
"""

import re
import unicodedata
from typing import Tuple, Dict, Any, List

class AgriculturalIntentClassifier:
    """
    Multilingual Semantic Intent Classifier for Indian Agricultural Queries.
    Supports 14 categories:
      1. crop_cultivation: Crop cultivation & crop selection
      2. fertilizer_soil: Fertilizers, nutrients & soil health
      3. crop_diseases: Crop diseases & symptoms
      4. pest_management: Pest & insect management
      5. irrigation_water: Irrigation & water management
      6. seeds_treatment: Seeds & seed treatment
      7. sowing_harvesting: Sowing, planting & harvesting methods
      8. weather_climate: Weather, rainfall & climate advice
      9. mandi_prices: Mandi prices & crop selling information
      10. govt_schemes: Government schemes & subsidies
      11. organic_farming: Organic farming & natural inputs (Jeevamrutha, etc.)
      12. equipment_technology: Farm equipment, machinery & agri-tech
      13. yield_profit: Crop yield, cost of cultivation & profit calculations
      14. general_agriculture: Other agricultural inquiries
    """

    CATEGORIES = {
        'crop_cultivation': {
            'id': 1,
            'name': 'Crop Cultivation & Selection',
            'keywords': [
                'cultivation', 'how to grow', 'farming method', 'crop selection', 'best crop', 'which crop', 'season',
                # Tamil
                'சாகுபடி', 'பயிர் தேர்வு', 'எந்த பயிர்', 'பயிர் செய்வது எப்படி', 'பருவம்', 'பயிர்',
                # Kannada
                'ಬೇಸಾಯ', 'ಬೆಳೆ ಆಯ್ಕೆ', 'ಯಾವ ಬೆಳೆ', 'ಬೆಳೆಯುವುದು ಹೇಗೆ', 'ಬೆಳೆಯ ವಿಧಾನ', 'ಬೆಳೆಯುವ ವಿದ್ಯೆ', 'ಬೆಳೆಯುವ ವಿಧಾನ', 'ಬೇಸಾಯ ಕ್ರಮ', 'ಕೃಷಿ ವಿಧಾನ', 'ಕೃಷಿ ವಿದ್ಯೆ', 'ಬೆಳೆಯುವುದು', 'ಹಂಗಾಮು',
                # Telugu
                'సాగు', 'పంట ఎంపిక', 'ఏ పంట', 'సాగు విధానం', 'సీజన్',
                # Hindi
                'खेती', 'फसल चयन', 'कौन सी फसल', 'बुआई', 'फसल कैसे उगाएं', 'ऋतु',
                # Malayalam
                'കൃഷി രീതി', 'ഏത് വിള', 'വിള തിരഞ്ഞെടുപ്പ്',
                # Bengali
                'চাষ', 'কোন ফসল', 'ফসল নির্বাচন',
                # Marathi
                'लागवड', 'पीक निवड', 'कोणते पीक', 'शेती पद्धत',
                # Gujarati
                'ખેતી પદ્ધતિ', 'કયો પાક', 'પાકની પસંદગી',
                # Punjabi
                'ਖੇਤੀਬਾੜੀ', 'ਕਿਹੜੀ ਫਸਲ', 'ਫਸਲ ਦੀ ਚੋਣ'
            ]
        },
        'fertilizer_soil': {
            'id': 2,
            'name': 'Fertilizers, Nutrients & Soil Health',
            'keywords': [
                'fertilizer', 'nutrient', 'urea', 'dap', 'npk', 'potash', 'zinc', 'boron', 'soil health', 'soil test', 'deficiency',
                # Tamil
                'உரம்', 'யூரியா', 'டிஏபி', 'பொட்டாஷ்', 'மண் பரிசோதனை', 'நுண்ணூட்டம்', 'தழைச்சத்து', 'மணிச்சத்து', 'சாம்பல் சத்து',
                # Kannada
                'ಗೊಬ್ಬರ', 'ರಸಗೊಬ್ಬರ', 'ಯೂರಿಯಾ', 'ಡಿಎಪಿ', 'ಪೊಟ್ಯಾಶ್', 'ಎನ್‌ಪಿಕೆ', 'ಮಣ್ಣು ಪರೀಕ್ಷೆ', 'ಪೋಷಕಾಂಶ', 'ಸತು',
                # Telugu
                'ఎరువులు', 'యూరియా', 'డీఏపీ', 'పొటాష్', 'మట్టి పరీక్ష', 'పోషకాలు',
                # Hindi
                'उर्वरक', 'खाद', 'यूरिया', 'डीएपी', 'पोटाश', 'मृदा स्वास्थ्य', 'मिट्टी परीक्षण', 'पोषक तत्व',
                # Malayalam
                'വളം', 'യൂറിയ', 'മണ്ണ് പരിശോധന', 'പോഷകങ്ങൾ',
                # Bengali
                'সার', 'ইউরিয়া', 'মাটি পরীক্ষা', 'পুষ্টি',
                # Marathi
                'खत', 'युरिया', 'डीएपी', 'माती परीक्षण', 'पोषकद्रव्ये',
                # Gujarati
                'ખાતર', 'યૂરિયા', 'જમીન ચકાસણી', 'પોષક તત્વો',
                # Punjabi
                'ਖਾਦ', 'ਯੂਰੀਆ', 'ਮਿੱਟੀ ਦੀ ਪਰਖ', 'ਪੋਸ਼ਕ ਤੱਤ'
            ]
        },
        'crop_diseases': {
            'id': 3,
            'name': 'Crop Diseases & Symptoms',
            'keywords': [
                'disease', 'blast', 'blight', 'rot', 'wilt', 'fungus', 'virus', 'yellow leaves', 'brown spot', 'leaf curl', 'leaf spot', 'symptom',
                # Tamil
                'நோய்', 'நோயை', 'நோயின்', 'நோயால்', 'குலை நோய்', 'குலை நோய', 'இலைக்கருகல்', 'அழுகல்', 'வாடல்', 'மஞ்சள் இலை', 'புள்ளி', 'இலைச்சுருள்', 'கருகல்', 'தண்டு அழுகல்', 'மடக்கு நோய்',
                # Kannada
                'ರೋಗ', 'ಬೆಂಕಿ ರೋಗ', 'ಬ್ಲಾಸ್ಟ್', 'ಕೊಳೆ ರೋಗ', 'ಎಲೆ ಕಲೆ', 'ಎಲೆ ಹಳದಿ', 'ಎಲೆ ಸುರುಟು', 'ಬಾಡುವ ರೋಗ', 'ಶಿಲೀಂಧ್ರ',
                # Telugu
                'తెగులు', 'అగ్గితెగులు', 'ఆకుమచ్చ', 'కుళ్ళు తెగులు', 'పసుపు ఆకులు', 'ఆకుముడుత',
                # Hindi
                'रोग', 'झुलसा', 'ब्लास्ट', 'सड़न', 'पीली पत्ती', 'धब्बा', 'उकठा', 'पत्ती मरोड़',
                # Malayalam
                'രോഗം', 'കുമിൾ', 'ഇലപ്പുള്ളി', 'വാട്ടം', 'മഞ്ഞളിപ്പ്',
                # Bengali
                'রোগ', 'ব্লাস্ট', 'ধসা', 'পচা', 'হলুদ পাতা',
                # Marathi
                'रोग', 'करपा', 'मर रोग', 'पाने पिवळी', 'कुजणे',
                # Gujarati
                'રોગ', 'ગેરુ', 'કરપો', 'સડો', 'સુકારો',
                # Punjabi
                'ਰੋਗ', 'ਬਿਮਾਰੀ', 'ਝੁਲਸ ਰੋਗ', 'ਸੜਾਂਦ', 'ਪੀਲੇ ਪੱਤੇ'
            ]
        },
        'pest_management': {
            'id': 4,
            'name': 'Pest & Insect Management',
            'keywords': [
                'pest', 'insect', 'caterpillar', 'borer', 'bollworm', 'aphid', 'thrips', 'whitefly', 'stem borer', 'pesticide', 'spray',
                # Tamil
                'பூச்சி', 'புழு', 'துளைப்பான்', 'காய்ப்புழு', 'அசுவினி', 'இலைப்பேன்', 'வெள்ளை ஈ', 'பூச்சிக்கொல்லி',
                # Kannada
                'ಕೀಟ', 'ಹುಳು', 'ಕಾಂಡ ಕೊರೆಯುವ', 'ಕಾಯಿ ಕೊರೆಯುವ', 'ನುಸಿ', 'ಬಿಳಿ ನೊಣ', 'ಜಿಗಿ ಹುಳು', 'ಕೀಟನಾಶಕ', 'ಸಿಂಪಡಣೆ',
                # Telugu
                'పురుగు', 'కీటకాలు', 'కాండం తొలిచే', 'గులాబీ పురుగు', 'తెల్లదోమ', 'పురుగుమందు',
                # Hindi
                'कीट', 'कीड़ा', 'सुंडी', 'छेदक', 'माहू', 'सफेद मक्खी', 'कीटनाशक', 'छिड़काव',
                # Malayalam
                'കീടം', 'പുഴു', 'തുരപ്പൻ', 'കീടനാശിനി',
                # Bengali
                'কীটপতঙ্গ', 'পোকা', 'শুঁয়োপোকা', 'কীটনাশক',
                # Marathi
                'कीड', 'अळी', 'बोंडअळी', 'खोडकिडा', 'मावा', 'तुडतुडे', 'कीटकनाशक',
                # Gujarati
                'જીવાત', 'ઇયળ', 'ચૂસિયા', 'કીટનાશક',
                # Punjabi
                'ਕੀੜੇ', 'ਸੁੰਡੀ', 'ਤੇਲਾ', 'ਕੀਟਨਾਸ਼ਕ'
            ]
        },
        'irrigation_water': {
            'id': 5,
            'name': 'Irrigation & Water Management',
            'keywords': [
                'irrigation', 'water', 'drip', 'sprinkler', 'watering schedule', 'water saving', 'borewell', 'water requirement',
                # Tamil
                'பாசனம்', 'தண்ணீர்', 'சொட்டு நீர்', 'தெளிப்பு நீர்', 'நீர் பாய்ச்சுதல்', 'நீர் சேமிப்பு',
                # Kannada
                'ನೀರಾವರಿ', 'ನೀರು', 'ಹನಿ ನೀರಾವರಿ', 'ತುಂತುರು', 'ನೀರು ಉಳಿತಾಯ', 'ನೀರಿನ ಪ್ರಮಾಣ',
                # Telugu
                'నీటిపారుదల', 'నీరు', 'బిందు సేద్యం', 'తుంపర సేద్యం', 'తడి',
                # Hindi
                'सिंचाई', 'पानी', 'ड्रिप', 'फव्वारा', 'जल प्रबंधन', 'जल संरक्षण',
                # Malayalam
                'നനയ്ക്കൽ', 'ജലസേചനം', 'ഡ്രിപ്പ്',
                # Bengali
                'সেচ', 'জল', 'ড্রিপ সেচ',
                # Marathi
                'पाणी व्यवस्थापन', 'सिंचन', 'ठिबक सिंचन', 'तुषार सिंचन',
                # Gujarati
                'પિયત', 'પાણી', 'ટપક પદ્ધતિ', 'ફુવારા પદ્ધતિ',
                # Punjabi
                'ਸਿੰਚਾਈ', 'ਪਾਣੀ', 'ਡਰਿੱਪ ਸਿੰਚਾਈ', 'ਫੁਹਾਰਾ'
            ]
        },
        'seeds_treatment': {
            'id': 6,
            'name': 'Seeds & Seed Treatment',
            'keywords': [
                'seed', 'seed rate', 'seed treatment', 'germination', 'hybrid seed', 'certified seed', 'seed soaking',
                # Tamil
                'விதை', 'விதை நேர்த்தி', 'முளைப்புத்திறன்', 'விதை அளவு', 'வீரிய விதை',
                # Kannada
                'ಬೀಜ', 'ಬೀಜೋಪಚಾರ', 'ಮೊಳಕೆ', 'ಬೀಜದ ಪ್ರಮಾಣ', 'ಹೈಬ್ರಿಡ್ ಬೀಜ',
                # Telugu
                'విత్తనం', 'విత్తన శుద్ధి', 'మొలక శాతం', 'విత్తన మోతాదు',
                # Hindi
                'बीज', 'बीजोपचार', 'अंकुरण', 'बीज दर', 'संकर बीज',
                # Malayalam
                'വിത്ത്', 'വിത്ത് പരിചരണം', 'മുളയ്ക്കൽ',
                # Bengali
                'বীজ', 'বীজ শোধন', 'অঙ্কুরোদগম',
                # Marathi
                'बियाणे', 'बीजप्रक्रिया', 'उगवण क्षमता', 'बियाण्याचे प्रमाण',
                # Gujarati
                'બિયારણ', 'બીજ માવજત', 'ઉગાવો',
                # Punjabi
                'ਬੀਜ', 'ਬੀਜ ਸੋਧ', 'ਜੰਮਣ ਸ਼ਕਤੀ'
            ]
        },
        'sowing_harvesting': {
            'id': 7,
            'name': 'Sowing & Harvesting Methods',
            'keywords': [
                'sowing', 'planting', 'transplanting', 'spacing', 'harvesting', 'harvest time', 'reaping', 'threshing',
                # Tamil
                'விதைப்பு', 'நடவு', 'இடைவெளி', 'அறுவடை', 'அறுவடை காலம்',
                # Kannada
                'ಬಿತ್ತನೆ', 'ನಾಟಿ', 'ಸಾಲುಗಳ ಅಂತರ', 'ಕಟಾವು', 'ಕೊಯ್ಲು',
                # Telugu
                'విత్తడం', 'నాట్లు', 'దూరం', 'కోత', 'పంట కోత',
                # Hindi
                'बुवाई', 'रोपाई', 'दूरी', 'कटाई', 'गहाई',
                # Malayalam
                'നടീൽ', 'വിളവെടുപ്പ്', 'അകലം',
                # Bengali
                'বপন', 'রোপণ', 'ফসল কাটা',
                # Marathi
                'पेरणी', 'टोकण', 'पुनर्लागवड', 'कापणी', 'मळणी',
                # Gujarati
                'વાવણી', 'રોપણી', 'કાપણી',
                # Punjabi
                'ਬਿਜਾਈ', 'ਪਨੀਰੀ', 'ਵਾਢੀ'
            ]
        },
        'weather_climate': {
            'id': 8,
            'name': 'Weather & Climate Advice',
            'keywords': [
                'weather', 'rain', 'rainfall', 'monsoon', 'temperature', 'frost', 'humidity', 'drought', 'storm',
                # Tamil
                'வானிலை', 'மழை', 'வெப்பம்', 'பனி', 'ஈரப்பதம்', 'வறட்சி', 'புயல்',
                # Kannada
                'ಹವಾಮಾನ', 'ಮಳೆ', 'ತಾಪಮಾನ', 'ಬಿಸಿಲು', 'ಚಳಿ', 'ಹಿಮ', 'ಬರಗಾಲ',
                # Telugu
                'వాతావరణం', 'వర్షం', 'ఉష్ణోగ్రత', 'మంచు', 'తుఫాను',
                # Hindi
                'मौसम', 'बारिश', 'वर्षा', 'तापमान', 'पाला', 'ओलावृष्टि', 'मानसून', 'सूखा',
                # Malayalam
                'കാലാവസ്ഥ', 'മഴ', 'ചൂട്',
                # Bengali
                'আবহাওয়া', 'বৃষ্টি', 'তাপমাত্রা',
                # Marathi
                'हवामान', 'पाऊस', 'तापमान', 'गारपीट', 'धुके',
                # Gujarati
                'હવામાન', 'વરસાદ', 'ગરમી', 'ઠંડી',
                # Punjabi
                'ਮੌਸਮ', 'ਮੀਂਹ', 'ਤਾਪਮਾਨ', 'ਕੋਰਾ'
            ]
        },
        'mandi_prices': {
            'id': 9,
            'name': 'Mandi Prices & Crop Selling',
            'keywords': [
                'mandi', 'price', 'rate', 'apmc', 'market price', 'modal price', 'sell crop', 'msp', 'commodity price', 'wholesale',
                # Tamil
                'மண்டி', 'விலை', 'சந்தை', 'விற்பனை', 'ரேட்', 'குறைந்தபட்ச ஆதரவு விலை', 'APMC',
                # Kannada
                'ಮಂಡಿ', 'ಬೆಲೆ', 'ದರ', 'ಮಾರುಕಟ್ಟೆ', 'ಮಾರಾಟ', 'ರೇಟು', 'ಬೆಂಬಲ ಬೆಲೆ', 'ಎಪಿಎಂಸಿ',
                # Telugu
                'మండి', 'ధర', 'మార్కెట్', 'రేటు', 'అమ్మకం', 'మద్దతు ధర',
                # Hindi
                'मंडी', 'भाव', 'दाम', 'रेट', 'बाजार', 'बिक्री', 'एमएसपी', 'न्यूनतम समर्थन मूल्य',
                # Malayalam
                'വിപണി വില', 'ചന്ത', 'വില', 'മാർക്കറ്റ്',
                # Bengali
                'মান্ডি', 'দর', 'দাম', 'বাজার দর',
                # Marathi
                'बाजारभाव', 'मंडी', 'दर', 'भाव', 'हमीभाव',
                # Gujarati
                'મંડી', 'ભાવ', 'બજાર ભાવ', 'ટેકાના ભાવ',
                # Punjabi
                'ਮੰਡੀ ਭਾਅ', 'ਰੇਟ', 'ਭਾਅ', 'ਸਰਕਾਰੀ ਰੇਟ'
            ]
        },
        'govt_schemes': {
            'id': 10,
            'name': 'Government Schemes & Subsidies',
            'keywords': [
                'scheme', 'subsidy', 'pm kisan', 'pmfby', 'insurance', 'loan', 'kcc', 'kisan credit', 'government benefit', 'portal',
                # Tamil
                'திட்டம்', 'மானியம்', 'பிஎம் கிசான்', 'காப்பீடு', 'கடன்', 'அரசு உதவி',
                # Kannada
                'ಯೋಜನೆ', 'ಸಹಾಯಧನ', 'ಸಬ್ಸಿಡಿ', 'ಪಿಎಂ ಕಿಸಾನ್', 'ವಿಮೆ', 'ಸಾಲ', 'ಸರ್ಕಾರಿ ಯೋಜನೆ', 'ಫ್ರೂಟ್ಸ್',
                # Telugu
                'పథకం', 'సబ్సిడీ', 'పీఎం కిసాన్', 'భీమా', 'రుణం', 'రైతు బంధు',
                # Hindi
                'योजना', 'सब्सिडी', 'अनुदान', 'पीएम किसान', 'फसल बीमा', 'ऋण', 'केसीसी',
                # Malayalam
                'പദ്ധതി', 'സബ്സിഡി', 'ഇൻഷുറൻസ്',
                # Bengali
                'প্রকল্প', 'ভর্তুকি', 'বীমা', 'ঋণ',
                # Marathi
                'योजना', 'अनुदान', 'पीक विमा', 'कर्ज',
                # Gujarati
                'યોજના', 'સબસિડી', 'વીમો', 'ધિરાણ',
                # Punjabi
                'ਸਕੀਮ', 'ਸਬਸਿਡੀ', 'ਬੀਮਾ', 'ਕਰਜ਼ਾ'
            ]
        },
        'organic_farming': {
            'id': 11,
            'name': 'Organic & Natural Farming',
            'keywords': [
                'organic', 'natural farming', 'jeevamrutha', 'panchagavya', 'compost', 'vermicompost', 'biofertilizer', 'cow dung', 'cow urine', 'neem',
                # Tamil
                'இயற்கை விவசாயம்', 'ஜீவாமிர்தம்', 'பஞ்சகாவ்யா', 'மண்புழு உரம்', 'தொழுஉரம்', 'நாட்டு மாடு',
                # Kannada
                'ಸಾವಯವ', 'ನೈಸರ್ಗಿಕ ಕೃಷಿ', 'ಜೀವಾಮೃತ', 'ಪಂಚಗವ್ಯ', 'ಎರೆಹುಳು ಗೊಬ್ಬರ', 'ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ', 'ಕಷಾಯ',
                # Telugu
                'సేంద్రీయ', 'ప్రకృతి వ్యవసాయం', 'జీవామృతం', 'పంచగవ్య', 'వర్మీ కంపోస్ట్',
                # Hindi
                'जैविक खेती', 'प्राकृतिक खेती', 'जीवामृत', 'पंचगव्य', 'केंचुआ खाद', 'वर्मीकम्पोस्ट', 'गोबर',
                # Malayalam
                'ജൈവകൃഷി', 'ജീവാമൃതം', 'പഞ്ചഗവ്യം',
                # Bengali
                'জৈব চাষ', 'প্রাকৃতিক চাষ', 'জীবামৃত',
                # Marathi
                'सेंद्रिय शेती', 'नैसर्गिक शेती', 'जीवामृत', 'पंचगव्य', 'गांडूळ खत',
                # Gujarati
                'પ્રાકૃતિક ખેતી', 'સજીવ ખેતી', 'જીવામૃત', 'વર્મીકમ્પોસ્ટ',
                # Punjabi
                'ਕੁਦਰਤੀ ਖੇਤੀ', 'ਜੈਵਿਕ ਖੇਤੀ', 'ਜੀਵਾਮ੍ਰਿਤ'
            ]
        },
        'equipment_technology': {
            'id': 12,
            'name': 'Farm Equipment & Technology',
            'keywords': [
                'tractor', 'rotavator', 'harvester', 'equipment', 'machinery', 'drone', 'sensor', 'solar pump', 'sprayer', 'weeder',
                # Tamil
                'டிராக்டர்', 'இயந்திரம்', 'கருவிகள்', 'ட்ரோன்', 'சோலார் பம்ப்', 'களை எடுக்கும் கருவி',
                # Kannada
                'ಟ್ರಾಕ್ಟರ್', 'ಯಂತ್ರೋಪಕರಣ', 'ಕೃಷಿ ಉಪಕರಣ', 'ಡ್ರೋನ್', 'ಸೋಲಾರ್ ಪಂಪ್', 'ಕಳೆ ಕೀಳುವ ಯಂತ್ರ',
                # Telugu
                'ట్రాక్టర్', 'యంత్రాలు', 'పరికరాలు', 'డ్రోన్', 'సోలార్ పంపు',
                # Hindi
                'ट्रैक्टर', 'यंत्र', 'कृषि उपकरण', 'मशीन', 'ड्रोन', 'सोलर पंप', 'रोटावेटर',
                # Malayalam
                'ട്രാക്ടർ', 'യന്ത്രങ്ങൾ',
                # Bengali
                'ট্রাক্টর', 'যন্ত্রপাতি',
                # Marathi
                'ट्रॅक्टर', 'यंत्रे', 'अवजारे', 'ड्रोन',
                # Gujarati
                'ટ્રેક્ટર', 'સાધનો', 'ઓજારો',
                # Punjabi
                'ਟਰੈਕਟਰ', 'ਸੰਦ', 'ਮਸ਼ੀਨਰੀ'
            ]
        },
        'yield_profit': {
            'id': 13,
            'name': 'Crop Yield & Profit Calculations',
            'keywords': [
                'yield', 'profit', 'cost of cultivation', 'quintal per acre', 'income', 'loss', 'calculation', 'margin', 'returns',
                # Tamil
                'மகசூல்', 'லாபம்', 'வருமானம்', 'செலவு', 'கணக்கீடு', 'ஏக்கருக்கு',
                # Kannada
                'ಇಳುವರಿ', 'ಲಾಭ', 'ಆದಾಯ', 'ವೆಚ್ಚ', 'ಎಕರೆಗೆ', 'ಲೆಕ್ಕಾಚಾರ',
                # Telugu
                'దిగుబడి', 'లాభం', 'ఆదాయం', 'ఖర్చు', 'ఎకరాకు',
                # Hindi
                'उपज', 'पैदावार', 'मुनाफा', 'लाभ', 'लागत', 'आमदनी', 'प्रति एकड़',
                # Malayalam
                'വിളവ്', 'ലാഭം', 'ചെലവ്',
                # Bengali
                'ফলন', 'লাভ', 'আয়',
                # Marathi
                'उत्पादन', 'नफा', 'उत्पन्न', 'खर्च', 'एकर',
                # Gujarati
                'ઉત્પાદન', 'નફો', 'આવક', 'ખર્ચ',
                # Punjabi
                'ਝਾੜ', 'ਮੁਨਾਫਾ', 'ਆਮਦਨ', 'ਖਰਚਾ'
            ]
        },
        'general_agriculture': {
            'id': 14,
            'name': 'General Agricultural Information',
            'keywords': [
                'agriculture', 'farmer', 'krishi', 'kisan', 'uzhavar', 'farming', 'kvk', 'university', 'officer',
                # Tamil
                'விவசாயம்', 'விவசாயி', 'உழவர்',
                # Kannada
                'ಕೃಷಿ', 'ರೈತ',
                # Telugu
                'వ్యవసాయం', 'రైతు',
                # Hindi
                'कृषि', 'किसान', 'खेती किसानी',
                # Malayalam
                'കൃഷി', 'കർഷകൻ',
                # Bengali
                'কৃষি', 'কৃষক',
                # Marathi
                'शेती', 'शेतकरी',
                # Gujarati
                'ખેતી', 'ખેડૂત',
                # Punjabi
                'ਖੇਤੀ', 'ਕਿਸਾਨ'
            ]
        }
    }

    # Language Script Detection Maps
    UNICODE_SCRIPT_RANGES = [
        ('ta', 0x0B80, 0x0BFF),  # Tamil
        ('kn', 0x0C80, 0x0CFF),  # Kannada
        ('te', 0x0C00, 0x0C7F),  # Telugu
        ('ml', 0x0D00, 0x0D7F),  # Malayalam
        ('bn', 0x0980, 0x09FF),  # Bengali
        ('gu', 0x0A80, 0x0AFF),  # Gujarati
        ('pa', 0x0A00, 0x0A7F),  # Punjabi (Gurmukhi)
        ('hi_mr', 0x0900, 0x097F), # Devanagari (Hindi or Marathi)
    ]

    MARATHI_MARKERS = {'आहे', 'नाही', 'पिकावर', 'शेतकरी', 'करपा', 'भातावर', 'कसे', 'करावे', 'एकरी', 'पाने', 'झाले'}

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Automatically identifies the primary Indian language of the text
        using native Unicode script frequency and marker analysis.
        Returns ISO code: 'kn', 'ta', 'te', 'hi', 'ml', 'bn', 'mr', 'gu', 'pa', or 'en'.
        """
        if not text:
            return 'en'

        counts = {lang: 0 for lang, _, _ in cls.UNICODE_SCRIPT_RANGES}
        total_indic = 0

        for ch in text:
            cp = ord(ch)
            for lang, start, end in cls.UNICODE_SCRIPT_RANGES:
                if start <= cp <= end:
                    counts[lang] += 1
                    total_indic += 1
                    break

        if total_indic > 0:
            top_script = max(counts, key=counts.get)
            if top_script == 'hi_mr':
                # Distinguish Marathi from Hindi
                tokens = set(text.lower().split())
                if tokens.intersection(cls.MARATHI_MARKERS):
                    return 'mr'
                return 'hi'
            return top_script

        # Fallback for Romanized text
        lower = text.lower()
        def has_word(word_list):
            return any(re.search(r'\b' + re.escape(w) + r'\b', lower) for w in word_list)

        if has_word(['vanakkam', 'thambi', 'nellu', 'payir', 'urame']):
            return 'ta'
        if has_word(['namaskara', 'bhatta', 'ragi', 'gobbarada', 'neeru']):
            return 'kn'
        if has_word(['namaskaram', 'panta', 'eruvulu']):
            return 'te'
        if has_word(['namaste', 'kisan', 'kheti', 'gehun', 'dhan', 'fasal', 'khad']):
            return 'hi'

        return 'en'

    @classmethod
    def classify(cls, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """
        Multilingual semantic classification of agricultural query.
        Returns:
            (category_key, category_metadata)
        """
        normalized = prompt.lower().strip()
        scores = {cat_key: 0 for cat_key in cls.CATEGORIES}

        # 1. Mandi Price High-Priority Routing
        mandi_markers = ['mandi', 'price', 'rate', 'bhav', 'விலை', 'மண்டி', 'ಬೆಲೆ', 'ದರ', 'ಮಂಡಿ', 'ధర', 'మండి', 'ભાવ', 'भाव', 'দর']
        has_mandi_word = any(
            re.search(r'\b' + re.escape(w) + r'\b', normalized) if w.isascii() else (w in normalized)
            for w in mandi_markers
        )
        if has_mandi_word:
            scores['mandi_prices'] += 12

        # 2. Yield & Profit Calculation High-Priority Routing
        has_yield_profit = any(
            re.search(r'\b' + re.escape(w) + r'\b', normalized) if w.isascii() else (w in normalized)
            for w in ['profit', 'net profit', 'cost of cultivation', 'calculate', 'income', 'ಲಾಭ', 'ಇಳುವರಿ', 'ಲೆಕ್ಕಾಚಾರ', 'லாபம்', 'மகசூல்', 'मुनाफा', 'लागत', 'आमदनी']
        )
        if has_yield_profit:
            scores['yield_profit'] += 12

        # 3. Disease vs Pest distinction
        has_disease_word = any(w in normalized for w in ['blast', 'blight', 'rot', 'wilt', 'disease', 'ರೋಗ', 'நோய்', 'తెగులు', 'रोग', 'ಕಲೆ', 'సుರುಟು'])
        if has_disease_word:
            scores['crop_diseases'] += 8

        has_pest_word = any(w in normalized for w in ['caterpillar', 'borer', 'bollworm', 'aphid', 'thrips', 'worm', 'ಹುಳು', 'ಕೀಟ', 'ಪುರುಗು', 'புழு', 'कीट', 'कीड़ा', 'సుಂಡಿ'])
        if has_pest_word:
            scores['pest_management'] += 8

        # 3. Fertilizer vs Organic
        has_organic_word = any(w in normalized for w in ['jeevamrutha', 'panchagavya', 'organic', 'natural farming', 'cow dung', 'ಜೀವಾಮೃತ', 'ಪಂಚಗವ್ಯ', 'ಸಾವಯವ', 'ஜீவாமிர்தம்', 'जीवामृत', 'जैविक'])
        if has_organic_word:
            scores['organic_farming'] += 10

        # 4. Standard keyword scoring across all 14 categories
        for cat_key, cat_data in cls.CATEGORIES.items():
            for kw in cat_data['keywords']:
                if kw.lower() in normalized:
                    # Longer phrases receive more weight
                    weight = 3 if len(kw.split()) > 1 else 2
                    scores[cat_key] += weight

        # Find category with top score
        top_category = max(scores, key=scores.get)
        if scores[top_category] == 0:
            top_category = 'general_agriculture'

        return top_category, cls.CATEGORIES[top_category]
