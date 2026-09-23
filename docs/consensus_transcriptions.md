# Multi-Model Consensus Transcriptions & Collation

Generated from top-5 model consensus multiple sequence alignments across Latin, Greek, and Aramaic corpora.

## 1. Latin Minuscule (*Vat.lat.629* f. 3v)

- **Top Models:** google/gemini-3.1-pro-preview, anthropic/claude-opus-5, google/gemini-2.5-pro, anthropic/claude-opus-4.8, google/gemini-3.7-flash
- **Ground Truth Chars:** 3697
- **Consensus Chars:** 3713

### Consensus Stream (First 500 Chars)

```
columnaureauitulaingalgalismugitudediteiusquoxinierlmpsonauittuncquidaplagusuatespdixhodieinierlmnatusepphaquicunctaeordestruetydolatriahicgeminoelieglorificatspuplurimisatqmagnisuirtutusignisemicuitiordanistransitusuodiuisusrefrenatisundisretroconuertitaquashierichosterilefontedemersouasculosalisinfecunditatepduxitpuerosinsultantessibiuerbotradiditbestiisrepentedeuorandossanguineasaquasinnecemhostiumdecurrerefecitinterhecsterilemconceptioniubofecundauiteiusqfiliumortuumsuscitauitcibostempatamar...
```

## 2. Greek Majuscule (*Codex Marchalianus*, Vat.gr.2125 p. 11)

- **Top Models:** anthropic/claude-opus-4.8, x-ai/grok-4.6, openai/gpt-5.5, qwen/qwen3-vl-235b-thinking, xiaomi/mimo-v2.5
- **Ground Truth Chars:** 1372
- **Consensus Chars:** 1243

### Consensus Stream (First 500 Chars)

```
ΟΝΟΜΑΤΑΠΡΟΦΗΤΩΝΚΑΙΠΟΘΕΝΕΙΣΙΚΑΙΠΟΥΑΠΕΘΑΝΟΝΚΑΙΠΩΣΚΑΙΠΟΥΚΕΙΝΤΑΙΗΣΑΙΑΣΑΠΟΙΕΡΟΥΣΑΛΗΜΩΝΗΣΚΕΙΥΠΗΜΩΣΕΠΡΙΣΘΕΙΣΕΙΣΔΥΟΚΑΙΕΤΕΘΗΥΠΟΚΑΤΩΔΡΥΟΣΡΩΓΗΛΕΧΟΜΕΝΑΤΗΣΔΙΑΒΑΣΕΩΣΤΩΥΔΑΤΩΝΩΝΑΠΩΛΕΣΕΝΕΖΕΚΙΑΣΧΩΣΑΣΑΥΤΑΚΑΙΟΘΣΤΟΣΗΜΕΗΟΝΤΟΥΣΙΛΩΑΜΔΙΑΤΟΝΠΡΟΦΗΤΗΝΕΠΟΙΗΣΕΝΟΤΙΠΡΟΤΟΥΘΑΝΕΙΝΟΛΙΓΩΡΗΣΑΣΗΥΞΑΤΟΠΙΕΙΝΥΔΩΡΚΑΙΕΥΘΕΩΣΑΠΕΣΤΑΛΗΑΥΤΩΕΞΑΥΤΟΥΔΙΑΤΟΥΤΟΕΚΛΗΘΗΣΙΛΩΑΜΟΕΡΜΗΝΕΥΕΤΑΙΑΠΕΣΤΑΛΜΕΝΟΣΚΑΙΕΠΙΤΟΥΕΖΕΚΙΑΠΡΟΤΟΥΠΟΙΗΣΑΙΤΟΥΣΛΑΚΚΟΥΣΚΑΙΤΑΣΚΟΛΥΜΒΗΘΡΑΣΕΠΙΕΥΧΗΤΟΥΗΣΑΙΟΥΜΙΚΡΟΝΥΔΩΡΕΞΕΛΗΛΥΘΕΙΟΤΙΗΝΟΛΑΟΣΕΝΓΚΛΕΙΣΜΩΑΛΛΟΦΥΛΩΝΚΑΙΠΩΣΗΝΑΗΑΠΟΛΙΣΩΣΕΧΟΥΣΑΥΔΩΡΗΡΩΤΟΥΝΓ...
```

## 3. Aramaic (*4Q530* IR Run)

### Unit `4Q530_f13`
- Ground Truth (7 chars): `עלגננינ`
- Consensus (3 chars): `חמא`

### Unit `4Q530_f14`
- Ground Truth (6 chars): `נגבריא`
- Consensus (2 chars): `וו`

### Unit `4Q530_f15`
- Ground Truth (6 chars): `נאוהיה`
- Consensus (2 chars): `אנ`

### Unit `4Q530_f17`
- Ground Truth (15 chars): `בהונאאתהלכעמהונ`
- Consensus (4 chars): `חלוי`

### Unit `4Q530_f18`
- Ground Truth (12 chars): `סגייסבולוהוא`
- Consensus (6 chars): `יווסאי`

### Unit `4Q530_f1i+f1ii`
- Ground Truth (136 chars): `נללוטולצעראנהדיידינוכלביתפלטאדיאהכלהנפשתקטילינקבלנעלקטליהונומזעקנתאונמותכחדאונתנשיציאקצפשגיאואהוהדמכולחמאחרתלשכניחזותאואפעללכנשתגבריאלפמ`
- Consensus (61 chars): `ומניכילאנהאהודיבניבשראאכלואנויעיראויאמרלהורענלבליעאאחאאחוהיימ`

### Unit `4Q530_f20`
- Ground Truth (3 chars): `שקר`
- Consensus (1 chars): `ש`

### Unit `4Q530_f2i+3`
- Ground Truth (73 chars): `יותבהנשמיאעמיתמנונבכלהיתחשבובחשבנשניאלמנדישבעתיומיאאלנבמטרהונאלתחדונואלתל`
- Consensus (13 chars): `חזינחלישרולמא`

### Unit `4Q530_f2ii+6_12`
- Ground Truth (1061 chars): `עלמותנפשנאועלוכלחברוהיואוהיהאחויאנונזמאזיאמרלהגלגמיסוחובבסאפחאומתאמרדינעלנפשהוחיבאלטלרוזניאוחדועלוהיגבריאותבואתלטוקבלעלוהיבאדינחלמותריהונחלמינונדתשנתעיניהונמנהונוקמושנתעיניהונמנהונוקמוופתחועיניהונואתועלשמיחזהאבוהונובאדינחלמיהונאשתעיובכנשתחבריהוננפיליאואמרההיהגברואאנהבחלמיהויתחזאבליליאדנהאגנתהרבההותנציבהבכלמיניעעינולההואגננינוהואמשקינכלעעבגנתהדאכליומינושרשינרברביננפקומנעקרהונומנעעחדנפקותלתתשרשהיחזאהויתעדדילשנינדינורמנשמיננחתוחזאהויתעדדיאתכסיעפראבכלמיאונוראדלקבכלעעיפרדסאדנכלהולאדלקבעעאושרשוהיבארעאכדיהיאהותמתאבדהבלשנינדינורובמיאדימבולאעדכאסופחלמאבאדינשאללהונההיהפשרחלמהולאהשכחוגבריאלחויאלהחלמאואמרלעזזאלחלמאדנתנתנלחנוכלספרפרשאויפשורלנאחלמאבאדינענההוואאחוהיאוהיהואמרקדמגבריאאפאנהחזיתבחלמיבליליאדנגברואהאשלטנשמיאלארעאנחתוכרסוניחיטווקדישארבאיתבמאהמאינלהמשמשינאלפאלפינלהסגדינכלקדמוהיהואקאמינוארוספרינפתיחוודינאמירודינרבאבכתבכתיבוברושמרשימומלכרבאעלכלחיאובסראועלכלדישליטינעדכהסופחלמאוארודחלוכלגבריאונפיליאוקרומהויואתהלכנשתנפיליאוגבריאושלחוהיעלחנוכוחשבוואמרולהאזלעלוהידיארחתאתראדמיתאלכהדיקדמישמעתאקלהואמרלהדייחואלכהפשרחלמיאודיכלאמנחעמכפנוהיביצבאהנאיתיובהארבאביניהונ`
- Consensus (113 chars): `אלפאדיחמשינשבעינמחזואחזיתבאחזואהונעבידתכולאברבעבחזאעבדוואדיקמנשמיאוחזאקדישאוחרתאלהונמנשמיאהקלנחרבסוסואדיאעליהונצל`

### Unit `4Q530_f4`
- Ground Truth (11 chars): `נטבניתחשבוב`
- Consensus (1 chars): `ש`

### Unit `4Q530_f7ii`
- Ground Truth (354 chars): `הנעודקבעותארכתגבריאכעלעולינופרחבידוהיכעלכנשרלמדנחארעאועברעלאמנחלדוחלפלשהוינמדברארבאורחקמנהונלידפרדסקשטאוחזהיחנוכוזעקהואמרלהמהוימהלכהוענהלהמהויאשתלחתלתנאולכהתנינותלמהויכפשראלנאלתרינחלמיאונשמעלמליכוכלנפיליארעאהנהובלפשראדיתרינחלמיאדיכלמנימובמומתהונויתוסדעלמנדעוחכמהדיספרפרשאעלדברתדיננדעמנכפשרהונבאדינפשרחנוכחלמיאלמהויואמרלהעלגננינדימנשמיננחתואנונעירינדינחתו`
- Consensus (35 chars): `באתראדנבערליאמשגיבינמנשמיננחתווילוא`

