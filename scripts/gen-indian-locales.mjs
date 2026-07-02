import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const localesDir = path.join(__dirname, '../src/locales');

const en = JSON.parse(fs.readFileSync(path.join(localesDir, 'en.json'), 'utf8'));
const hi = JSON.parse(fs.readFileSync(path.join(localesDir, 'hi.json'), 'utf8'));

const langs = {
  'en-IN': null,
  bn: {
    brand: { tagline: 'মহিমার পিছনের গল্প', description: 'প্রিমিয়াম বৈশ্বিক ক্রীড়া কাহিনী — বায়োপিক, ডকুমেন্টারি, প্রতিদ্বন্দ্বিতা ও লাইভ কভারেজ।' },
    nav: { home: 'হোম', originals: 'অরিজিনাল', shorts: 'শর্টস', legends: 'কিংবদন্তি', rivalries: 'প্রতিদ্বন্দ্বিতা', stories: 'গল্প', secrets: 'রহস্য', events: 'ইভেন্ট', live: 'লাইভ', news: 'সংবাদ', explore: 'অন্বেষণ', membership: 'সদস্যতা', login: 'লগইন', logout: 'লগ আউট', profile: 'প্রোফাইল', watchlist: 'ওয়াচলিস্ট', app: 'অ্যাপ', more: 'আরও', browse: 'ব্রাউজ', help: 'সহায়তা' },
    selectors: { language: 'ভাষা', region: 'অঞ্চল', currency: 'মুদ্রা', indiaLanguages: 'ভারত', international: 'আন্তর্জাতিক' },
    hero: { watchNow: 'এখনই দেখুন', watchTrailer: 'ট্রেলার দেখুন', myList: 'আমার তালিকা', inList: 'তালিকায়', explore: 'অরিজিনাল দেখুন' },
    membership: { title: 'মহিমার পিছনের গল্প', subtitle: 'প্রিমিয়াম ক্রীড়া কাহিনীতে সীমাহীন অ্যাক্সেস।', free: 'বিনামূল্যে', premium: 'প্রিমিয়াম', vip: 'VIP', perMonth: '/মাস', perYear: '/বছর', pricedIn: '{{currency}}-তে মূল্য', startTrial: 'বিনামূল্যে ট্রায়াল', paymentMethods: 'পেমেন্ট পদ্ধতি', monthly: 'মাসিক', annual: 'বার্ষিক' },
    auth: { welcomeBack: 'স্বাগতম', signIn: 'সাইন ইন', signUp: 'অ্যাকাউন্ট তৈরি', email: 'ইমেইল', password: 'পাসওয়ার্ড', forgotPassword: 'পাসওয়ার্ড ভুলে গেছেন?', noAccount: 'অ্যাকাউন্ট নেই?', hasAccount: 'ইতিমধ্যে অ্যাকাউন্ট আছে?' },
    profile: { billing: 'বিলিং', upgrade: 'আপগ্রেড', signOut: 'সাইন আউট', watchlist: 'ওয়াচলিস্ট', continueWatching: 'দেখা চালিয়ে যান', settings: 'অ্যাকাউন্ট সেটিংস', help: 'সহায়তা কেন্দ্র' },
    footer: { navigation: 'নেভিগেশন', support: 'সহায়তা', legal: 'আইনি', subscribe: 'সাবস্ক্রাইব', privacy: 'গোপনীয়তা', terms: 'শর্তাবলী', help: 'সহায়তা', rights: 'সর্বস্বত্ব সংরক্ষিত।' },
    common: { viewAll: 'সব দেখুন', search: 'অনুসন্ধান', loading: 'লোড হচ্ছে…', save: 'সংরক্ষণ', cancel: 'বাতিল', back: 'পিছনে' },
    home: { trending: 'এখন ট্রেন্ডিং', continueWatching: 'দেখা চালিয়ে যান', originals: 'অরিজিনাল', shorts: 'শর্টস', legends: 'কিংবদন্তি', liveNow: 'এখন লাইভ' },
    rows: { top10Title: 'টপ ১০ স্পোর্টস ডকু', comingSoonTitle: 'শীঘ্রই আসছে', sportsLegends: 'ক্রীড়া কিংবদন্তি', bollywood: 'বলিউড', resume: 'চালিয়ে যান' },
    help: { title: 'সহায়তা কেন্দ্র', contactUs: 'যোগাযোগ করুন' },
    live: { title: 'UNTOLD লাইভ', schedule: 'আজকের সময়সূচী', remindMe: 'মনে করিয়ে দিন' },
    app: { title: 'যেকোনো জায়গায় দেখুন', comingSoon: 'শীঘ্রই আসছে' },
  },
  ta: {
    brand: { tagline: 'மகிமைக்குப் பின்னால் உள்ள கதை', description: 'பிரீமியம் உலகளாவிய விளையாட்டு கதைகள் — ஆவணப்படங்கள், பயோபிக், நேரடி ஒளிபரப்பு.' },
    nav: { home: 'முகப்பு', originals: 'ஒரிஜினல்ஸ்', shorts: 'ஷார்ட்ஸ்', legends: 'வீரர்கள்', rivalries: 'போட்டி', stories: 'கதைகள்', secrets: 'ரகசியங்கள்', events: 'நிகழ்வுகள்', live: 'நேரலை', news: 'செய்திகள்', explore: 'ஆராயுங்கள்', membership: 'உறுப்பினர்', login: 'உள்நுழை', logout: 'வெளியேறு', profile: 'சுயவிவரம்', watchlist: 'வாட்ச்லிஸ்ட்', app: 'ஆப்', more: 'மேலும்' },
    selectors: { language: 'மொழி', region: 'பிராந்தியம்', currency: 'நாணயம்', indiaLanguages: 'இந்தியா', international: 'சர்வதேச' },
    hero: { watchNow: 'இப்போது பாருங்கள்', watchTrailer: 'டிரெய்லர்', myList: 'என் பட்டியல்', inList: 'பட்டியலில்', explore: 'ஒரிஜினல்ஸ்' },
    membership: { title: 'மகிமைக்குப் பின்னால் உள்ள கதை', free: 'இலவசம்', premium: 'பிரீமியம்', vip: 'VIP', perMonth: '/மாதம்', pricedIn: '{{currency}}-இல் விலை', paymentMethods: 'கட்டண முறைகள்' },
    auth: { welcomeBack: 'மீண்டும் வரவேற்கிறோம்', signIn: 'உள்நுழை', signUp: 'கணக்கு உருவாக்கு', email: 'மின்னஞ்சல்', password: 'கடவுச்சொல்', forgotPassword: 'கடவுச்சொல் மறந்துவிட்டதா?' },
    footer: { navigation: 'வழிசெலுத்தல்', support: 'ஆதரவு', legal: 'சட்டம்', subscribe: 'சந்தா', privacy: 'தனியுரிமை', terms: 'விதிமுறைகள்', help: 'உதவி', rights: 'அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை.' },
    common: { viewAll: 'அனைத்தும்', search: 'தேடு', loading: 'ஏற்றுகிறது…' },
    home: { trending: 'இப்போது டிரெண்டிங்', continueWatching: 'தொடர்ந்து பாருங்கள்', liveNow: 'நேரலை' },
    rows: { top10Title: 'டாப் 10 விளையாட்டு', comingSoonTitle: 'விரைவில்', resume: 'தொடரவும்' },
    help: { title: 'உதவி மையம்', contactUs: 'எங்களை தொடர்பு கொள்ளுங்கள்' },
  },
  te: {
    brand: { tagline: 'గొప్పతనం వెనుక కథ', description: 'ప్రీమియం క్రీడా కథలు — డాక్యుమెంటరీలు, బయోపిక్, లైవ్ కవరేజ్.' },
    nav: { home: 'హోమ్', originals: 'ఒరిజినల్స్', shorts: 'షార్ట్స్', legends: 'లెజెండ్స్', live: 'లైవ్', membership: 'సభ్యత్వం', login: 'లాగిన్', profile: 'ప్రొఫైల్', watchlist: 'వాచ్‌లిస్ట్', app: 'యాప్', explore: 'అన్వేషించండి', more: 'మరిన్ని' },
    selectors: { language: 'భాష', indiaLanguages: 'భారతదేశం', international: 'అంతర్జాతీయ', currency: 'కరెన్సీ' },
    hero: { watchNow: 'ఇప్పుడే చూడండి', watchTrailer: 'ట్రైలర్', myList: 'నా జాబితా', explore: 'ఒరిజినల్స్' },
    membership: { free: 'ఉచితం', premium: 'ప్రీమియం', vip: 'VIP', perMonth: '/నెల', pricedIn: '{{currency}} లో ధరలు', paymentMethods: 'చెల్లింపు పద్ధతులు' },
    auth: { welcomeBack: 'స్వాగతం', signIn: 'సైన్ ఇన్', email: 'ఇమెయిల్', password: 'పాస్‌వర్డ్' },
    footer: { subscribe: 'సబ్‌స్క్రైబ్', privacy: 'గోప్యత', terms: 'నిబంధనలు', help: 'సహాయం', rights: 'అన్ని హక్కులు రిజర్వ్.' },
    common: { viewAll: 'అన్నీ చూడండి', search: 'వెతకండి', loading: 'లోడ్ అవుతోంది…' },
    rows: { top10Title: 'టాప్ 10 స్పోర్ట్స్', comingSoonTitle: 'త్వరలో', resume: 'కొనసాగించు' },
    help: { title: 'సహాయ కేంద్రం' },
  },
  mr: {
    brand: { tagline: 'महिमेच्या मागची कथा', description: 'प्रीमियम क्रीडा कथा — डॉक्युमेंट्री, बायोपिक, लाइव्ह कव्हरेज.' },
    nav: { home: 'होम', originals: 'ओरिजिनल्स', shorts: 'शॉर्ट्स', legends: 'महान खेळाडू', live: 'लाइव्ह', membership: 'सदस्यत्व', login: 'लॉगिन', profile: 'प्रोफाइल', watchlist: 'वॉचलिस्ट', app: 'अॅप', explore: 'शोधा' },
    selectors: { language: 'भाषा', indiaLanguages: 'भारत', international: 'आंतरराष्ट्रीय', currency: 'चलन' },
    hero: { watchNow: 'आत्ता पहा', watchTrailer: 'ट्रेलर', myList: 'माझी यादी', explore: 'ओरिजिनल्स' },
    membership: { free: 'मोफत', premium: 'प्रीमियम', vip: 'VIP', perMonth: '/महिना', pricedIn: '{{currency}} मध्ये किंमत', paymentMethods: 'पेमेंट पद्धती' },
    auth: { welcomeBack: 'पुन्हा स्वागत', signIn: 'साइन इन', email: 'ईमेल', password: 'पासवर्ड' },
    footer: { subscribe: 'सदस्यता', privacy: 'गोपनीयता', terms: 'अटी', help: 'मदत', rights: 'सर्व हक्क राखीव.' },
    common: { viewAll: 'सर्व पहा', search: 'शोध', loading: 'लोड होत आहे…' },
    rows: { top10Title: 'टॉप १० स्पोर्ट्स', comingSoonTitle: 'लवकरच', resume: 'पुन्हा सुरू' },
    help: { title: 'मदत केंद्र' },
  },
  gu: {
    brand: { tagline: 'મહિમાની પાછળની વાર્તા', description: 'પ્રીમિયમ રમતગમત વાર્તાઓ — ડોક્યુમેન્ટરી, બાયોપિક, લાઇવ કવરેજ.' },
    nav: { home: 'હોમ', originals: 'ઓરિજિનલ્સ', shorts: 'શોર્ટ્સ', legends: 'મહાન ખેલાડીઓ', live: 'લાઇવ', membership: 'સભ્યતા', login: 'લૉગિન', profile: 'પ્રોફાઇલ', watchlist: 'વૉચલિસ્ટ', app: 'એપ' },
    selectors: { language: 'ભાષા', indiaLanguages: 'ભારત', international: 'આંતરરાષ્ટ્રીય', currency: 'ચલણ' },
    hero: { watchNow: 'હવે જુઓ', watchTrailer: 'ટ્રેલર', myList: 'મારી યાદી', explore: 'ઓરિજિનલ્સ' },
    membership: { free: 'મફત', premium: 'પ્રીમિયમ', vip: 'VIP', perMonth: '/મહિનો', pricedIn: '{{currency}} માં કિંમત', paymentMethods: 'ચુકવણી પદ્ધતિઓ' },
    auth: { welcomeBack: 'પાછા સ્વાગત', signIn: 'સાઇન ઇન', email: 'ઇમેઇલ', password: 'પાસવર્ડ' },
    footer: { subscribe: 'સબ્સ્ક્રાઇબ', privacy: 'ગોપનીયતા', terms: 'નિયમો', help: 'મદદ', rights: 'સર્વાધિકાર સુરક્ષિત.' },
    common: { viewAll: 'બધું જુઓ', search: 'શોધો', loading: 'લોડ થઈ રહ્યું છે…' },
    rows: { top10Title: 'ટોપ ૧૦ સ્પોર્ટ્સ', comingSoonTitle: 'ટૂંક સમયમાં', resume: 'ચાલુ રાખો' },
    help: { title: 'મદદ કેન્દ્ર' },
  },
  kn: {
    brand: { tagline: 'ಮಹಿಮೆಯ ಹಿಂದಿನ ಕಥೆ', description: 'ಪ್ರೀಮಿಯಂ ಕ್ರೀಡಾ ಕಥೆಗಳು — ಡಾಕ್ಯುಮೆಂಟರಿ, ಬಯೋಪಿಕ್, ಲೈವ್ ಕವರೇಜ್.' },
    nav: { home: 'ಹೋಮ್', originals: 'ಒರಿಜಿನಲ್ಸ್', shorts: 'ಶಾರ್ಟ್ಸ್', legends: 'ದಿಗ್ಗಜರು', live: 'ಲೈವ್', membership: 'ಸದಸ್ಯತ್ವ', login: 'ಲಾಗಿನ್', profile: 'ಪ್ರೊಫೈಲ್', watchlist: 'ವಾಚ್‌ಲಿಸ್ಟ್', app: 'ಆ್ಯಪ್' },
    selectors: { language: 'ಭಾಷೆ', indiaLanguages: 'ಭಾರತ', international: 'ಅಂತರರಾಷ್ಟ್ರೀಯ', currency: 'ಕರೆನ್ಸಿ' },
    hero: { watchNow: 'ಈಗ ನೋಡಿ', watchTrailer: 'ಟ್ರೈಲರ್', myList: 'ನನ್ನ ಪಟ್ಟಿ', explore: 'ಒರಿಜಿನಲ್ಸ್' },
    membership: { free: 'ಉಚಿತ', premium: 'ಪ್ರೀಮಿಯಂ', vip: 'VIP', perMonth: '/ತಿಂಗಳು', pricedIn: '{{currency}} ನಲ್ಲಿ ಬೆಲೆ', paymentMethods: 'ಪಾವತಿ ವಿಧಾನಗಳು' },
    auth: { welcomeBack: 'ಮರಳಿ ಸ್ವಾಗತ', signIn: 'ಸೈನ್ ಇನ್', email: 'ಇಮೇಲ್', password: 'ಪಾಸ್‌ವರ್ಡ್' },
    footer: { subscribe: 'ಚಂದಾದಾರರಾಗಿ', privacy: 'ಗೌಪ್ಯತೆ', terms: 'ನಿಯಮಗಳು', help: 'ಸಹಾಯ', rights: 'ಎಲ್ಲಾ ಹಕ್ಕುಗಳು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ.' },
    common: { viewAll: 'ಎಲ್ಲಾ ನೋಡಿ', search: 'ಹುಡುಕಿ', loading: 'ಲೋಡ್ ಆಗುತ್ತಿದೆ…' },
    rows: { top10Title: 'ಟಾಪ್ ೧೦ ಸ್ಪೋರ್ಟ್ಸ್', comingSoonTitle: 'ಶೀಘ್ರದಲ್ಲೇ', resume: 'ಮುಂದುವರಿಸಿ' },
    help: { title: 'ಸಹಾಯ ಕೇಂದ್ರ' },
  },
  ml: {
    brand: { tagline: 'മഹത്വത്തിന് പിന്നിലെ കഥ', description: 'പ്രീമിയം കായിക കഥകൾ — ഡോക്യുമെന്ററി, ബയോപിക്, ലൈവ് കവറേജ്.' },
    nav: { home: 'ഹോം', originals: 'ഒറിജിനൽസ്', shorts: 'ഷോർട്സ്', legends: 'ദിഗ്ഗജന്മാർ', live: 'ലൈവ്', membership: 'അംഗത്വം', login: 'ലോഗിൻ', profile: 'പ്രൊഫൈൽ', watchlist: 'വാച്ച്‌ലിസ്റ്റ്', app: 'ആപ്പ്' },
    selectors: { language: 'ഭാഷ', indiaLanguages: 'ഇന്ത്യ', international: 'അന്താരാഷ്ട്ര', currency: 'കറൻസി' },
    hero: { watchNow: 'ഇപ്പോൾ കാണുക', watchTrailer: 'ട്രെയ്‌ലർ', myList: 'എന്റെ ലിസ്റ്റ്', explore: 'ഒറിജിനൽസ്' },
    membership: { free: 'സൗജന്യം', premium: 'പ്രീമിയം', vip: 'VIP', perMonth: '/മാസം', pricedIn: '{{currency}} ൽ വില', paymentMethods: 'പേയ്‌മെന്റ് രീതികൾ' },
    auth: { welcomeBack: 'തിരികെ സ്വാഗതം', signIn: 'സൈൻ ഇൻ', email: 'ഇമെയിൽ', password: 'പാസ്‌വേഡ്' },
    footer: { subscribe: 'സബ്‌സ്‌ക്രൈബ്', privacy: 'സ്വകാര്യത', terms: 'നിബന്ധനകൾ', help: 'സഹായം', rights: 'എല്ലാ അവകാശങ്ങളും നിക്ഷിപ്തം.' },
    common: { viewAll: 'എല്ലാം കാണുക', search: 'തിരയുക', loading: 'ലോഡ് ചെയ്യുന്നു…' },
    rows: { top10Title: 'ടോപ്പ് 10 സ്പോർട്സ്', comingSoonTitle: 'ഉടൻ', resume: 'തുടരുക' },
    help: { title: 'സഹായ കേന്ദ്രം' },
  },
  pa: {
    brand: { tagline: 'ਮਹਿਮਾ ਦੇ ਪਿੱਛੇ ਦੀ ਕਹਾਣੀ', description: 'ਪ੍ਰੀਮੀਅਮ ਖੇਡ ਕਹਾਣੀਆਂ — ਡਾਕੂਮੈਂਟਰੀ, ਬਾਇਓਪਿਕ, ਲਾਈਵ ਕਵਰੇਜ।' },
    nav: { home: 'ਹੋਮ', originals: 'ਓਰਿਜਿਨਲਜ਼', shorts: 'ਸ਼ਾਰਟਸ', legends: 'ਮਹਾਨ ਖਿਡਾਰੀ', live: 'ਲਾਈਵ', membership: 'ਮੈਂਬਰਸ਼ਿਪ', login: 'ਲੌਗਇਨ', profile: 'ਪ੍ਰੋਫਾਈਲ', watchlist: 'ਵਾਚਲਿਸਟ', app: 'ਐਪ' },
    selectors: { language: 'ਭਾਸ਼ਾ', indiaLanguages: 'ਭਾਰਤ', international: 'ਅੰਤਰਰਾਸ਼ਟਰੀ', currency: 'ਮੁਦਰਾ' },
    hero: { watchNow: 'ਹੁਣੇ ਦੇਖੋ', watchTrailer: 'ਟ੍ਰੇਲਰ', myList: 'ਮੇਰੀ ਸੂਚੀ', explore: 'ਓਰਿਜਿਨਲਜ਼' },
    membership: { free: 'ਮੁਫ਼ਤ', premium: 'ਪ੍ਰੀਮੀਅਮ', vip: 'VIP', perMonth: '/ਮਹੀਨਾ', pricedIn: '{{currency}} ਵਿੱਚ ਕੀਮਤ', paymentMethods: 'ਭੁਗਤਾਨ ਦੇ ਤਰੀਕੇ' },
    auth: { welcomeBack: 'ਵਾਪਸ ਸਵਾਗਤ', signIn: 'ਸਾਈਨ ਇਨ', email: 'ਈਮੇਲ', password: 'ਪਾਸਵਰਡ' },
    footer: { subscribe: 'ਸਬਸਕ੍ਰਾਈਬ', privacy: 'ਗੋਪਨੀਯਤਾ', terms: 'ਸ਼ਰਤਾਂ', help: 'ਮਦਦ', rights: 'ਸਾਰੇ ਅਧਿਕਾਰ ਸੁਰੱਖਿਤ।' },
    common: { viewAll: 'ਸਭ ਦੇਖੋ', search: 'ਖੋਜੋ', loading: 'ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ…' },
    rows: { top10Title: 'ਟਾਪ 10 ਸਪੋਰਟਸ', comingSoonTitle: 'ਜਲਦੀ', resume: 'ਜਾਰੀ ਰੱਖੋ' },
    help: { title: 'ਮਦਦ ਕੇਂਦਰ' },
  },
  ur: {
    brand: { tagline: 'عظمت کے پیچھے کی کہانی', description: 'پریمیم کھیلوں کی کہانیاں — دستاویزی فلمیں، بایوپک، لائیو کوریج۔' },
    nav: { home: 'ہوم', originals: 'اصل', shorts: 'شارٹس', legends: 'لیجنڈز', live: 'لائیو', membership: 'رکنیت', login: 'لاگ ان', profile: 'پروفائل', watchlist: 'واچ لسٹ', app: 'ایپ' },
    selectors: { language: 'زبان', indiaLanguages: 'بھارت', international: 'بین الاقوامی', currency: 'کرنسی' },
    hero: { watchNow: 'ابھی دیکھیں', watchTrailer: 'ٹریلر', myList: 'میری فہرست', explore: 'اصل' },
    membership: { free: 'مفت', premium: 'پریمیم', vip: 'VIP', perMonth: '/ماہ', pricedIn: '{{currency}} میں قیمتیں', paymentMethods: 'ادائیگی کے طریقے' },
    auth: { welcomeBack: 'خوش آمدید', signIn: 'سائن ان', email: 'ای میل', password: 'پاس ورڈ' },
    footer: { subscribe: 'سبسکرائب', privacy: 'رازداری', terms: 'شرائط', help: 'مدد', rights: 'جملہ حقوق محفوظ ہیں۔' },
    common: { viewAll: 'سب دیکھیں', search: 'تلاش', loading: 'لوڈ ہو رہا ہے…' },
    rows: { top10Title: 'ٹاپ 10 اسپورٹس', comingSoonTitle: 'جلد', resume: 'جاری رکھیں' },
    help: { title: 'مدد مرکز' },
  },
  or: {
    brand: { tagline: 'ମହିମା ପଛର କାହାଣୀ', description: 'ପ୍ରିମିୟମ କ୍ରୀଡା କାହାଣୀ — ଡକ୍ୟୁମେଣ୍ଟରୀ, ବାୟୋପିକ୍, ଲାଇଭ୍ କଭରେଜ୍।' },
    nav: { home: 'ହୋମ୍', originals: 'ଅରିଜିନାଲ୍ସ', shorts: 'ଶର୍ଟ୍ସ', legends: 'ମହାନ ଖେଳାଳି', live: 'ଲାଇଭ୍', membership: 'ସଦସ୍ୟତା', login: 'ଲଗଇନ୍', profile: 'ପ୍ରୋଫାଇଲ୍', watchlist: 'ୱାଚ୍‌ଲିଷ୍ଟ', app: 'ଆପ୍' },
    selectors: { language: 'ଭାଷା', indiaLanguages: 'ଭାରତ', international: 'ଆନ୍ତର୍ଜାତୀୟ', currency: 'ମୁଦ୍ରା' },
    hero: { watchNow: 'ବର୍ତ୍ତମାନ ଦେଖନ୍ତୁ', watchTrailer: 'ଟ୍ରେଲର୍', myList: 'ମୋ ତାଲିକା', explore: 'ଅରିଜିନାଲ୍ସ' },
    membership: { free: 'ମାଗଣା', premium: 'ପ୍ରିମିୟମ୍', vip: 'VIP', perMonth: '/ମାସ', pricedIn: '{{currency}} ରେ ମୂଲ୍ୟ', paymentMethods: 'ପେମେଣ୍ଟ ପଦ୍ଧତି' },
    auth: { welcomeBack: 'ପୁନର୍ବାର ସ୍ୱାଗତ', signIn: 'ସାଇନ୍ ଇନ୍', email: 'ଇମେଲ୍', password: 'ପାସୱାର୍ଡ' },
    footer: { subscribe: 'ସବସ୍କ୍ରାଇବ୍', privacy: 'ଗୋପନୀୟତା', terms: 'ନିୟମ', help: 'ସହାୟତା', rights: 'ସର୍ବସ୍ୱତ୍ୱ ସଂରକ୍ଷିତ।' },
    common: { viewAll: 'ସବୁ ଦେଖନ୍ତୁ', search: 'ଖୋଜନ୍ତୁ', loading: 'ଲୋଡ୍ ହେଉଛି…' },
    rows: { top10Title: 'ଟପ୍ ୧୦ ସ୍ପୋର୍ଟ୍ସ', comingSoonTitle: 'ଶୀଘ୍ର', resume: 'ଜାରି ରଖନ୍ତୁ' },
    help: { title: 'ସହାୟତା କେନ୍ଦ୍ର' },
  },
};

function merge(base, patch) {
  if (!patch) return JSON.parse(JSON.stringify(base));
  const result = { ...base };
  for (const [k, v] of Object.entries(patch)) {
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      result[k] = merge(base[k] || {}, v);
    } else {
      result[k] = v;
    }
  }
  return result;
}

const imports = [];
const exports = [];

for (const [code, patch] of Object.entries(langs)) {
  const merged = code === 'en-IN' ? en : merge(hi, patch);
  const file = path.join(localesDir, `${code}.json`);
  fs.writeFileSync(file, `${JSON.stringify(merged, null, 2)}\n`);
  const varName = code.replace(/-/g, '_');
  imports.push(`import ${varName} from './${code}.json';`);
  exports.push(`  '${code}': ${varName},`);
}

const indexContent = `${imports.join('\n')}

export const INDIAN_LOCALE_CODES = ${JSON.stringify(Object.keys(langs))};

export const indianLocales = {
${exports.join('\n')}
};
`;

fs.writeFileSync(path.join(localesDir, 'indianLocales.js'), indexContent);
console.log('Generated', Object.keys(langs).length, 'Indian locale files');
