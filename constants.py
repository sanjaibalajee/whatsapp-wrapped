# constants - stop words, patterns, static stuff

# system msgs to filter
SYSTEM_PATTERNS = [
    "Messages and calls are end-to-end encrypted",
    "created group",
    "added you",
    "left the group",
    "removed",
    "changed the group",
    "You're now an admin",
    "You're no longer an admin",
    "changed this group's icon",
    "deleted this group's icon",
    "changed the subject",
    "joined using this group's invite link",
]

# bots and system senders to exclude
IGNORED_SENDERS = [
    "Meta AI",
    "You",  # wa export uses "You" for your own msgs sometimes
]

# media patterns in wa exports
MEDIA_PATTERNS = {
    "image": "image omitted",
    "video": "video omitted",
    "audio": "audio omitted",
    "sticker": "sticker omitted",
    "gif": "GIF omitted",
    "document": "document omitted",
    "contact": "contact card omitted",
    "location": "location omitted",
}

# stop words - filter these from analysis
CHAT_STOP_WORDS = {
    # basic english
    'the', 'a', 'an', 'is', 'it', 'to', 'of', 'and', 'in', 'for', 'on',
    'with', 'as', 'at', 'by', 'this', 'that', 'i', 'you', 'he', 'she',
    'we', 'they', 'me', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
    'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
    'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'get', 'got',
    'but', 'or', 'if', 'then', 'so', 'just', 'now', 'here', 'there',
    'what', 'who', 'how', 'when', 'where', 'why', 'which', 'whom', 'whose',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'than', 'too', 'very',
    'any', 'much', 'many', 'else', 'either', 'neither', 'whether', 'ever',
    'once', 'twice', 'lot', 'lots', 'bit', 'little', 'less', 'least',

    # verbs
    'go', 'going', 'went', 'gone', 'come', 'came', 'coming', 'take', 'took',
    'taken', 'taking', 'make', 'made', 'making', 'get', 'got', 'getting',
    'see', 'saw', 'seen', 'seeing', 'know', 'knew', 'known', 'knowing',
    'think', 'thought', 'thinking', 'want', 'wanted', 'wanting',
    'say', 'said', 'saying', 'tell', 'told', 'telling', 'ask', 'asked',
    'try', 'tried', 'trying', 'let', 'put', 'give', 'gave', 'given',
    'look', 'looked', 'looking', 'find', 'found', 'finding',
    'use', 'used', 'using', 'keep', 'kept', 'keeping',
    'start', 'started', 'starting', 'stop', 'stopped', 'stopping',
    'send', 'sent', 'sending', 'read', 'reading', 'write', 'writing',
    'call', 'called', 'calling', 'reply', 'replied', 'replying',
    'wait', 'waiting', 'leave', 'left', 'leaving', 'stay', 'staying',
    'change', 'changed', 'changing', 'meet', 'met', 'meeting',
    'feel', 'felt', 'feeling', 'seems', 'seem', 'seemed',

    # adj/adv
    'good', 'bad', 'best', 'better', 'worse', 'worst', 'great', 'nice',
    'right', 'wrong', 'true', 'false', 'real', 'fake', 'new', 'old',
    'big', 'small', 'long', 'short', 'high', 'low', 'first', 'last',
    'next', 'early', 'late', 'fast', 'slow', 'easy', 'hard', 'sure',
    'well', 'back', 'even', 'still', 'also', 'again', 'already', 'always',
    'never', 'maybe', 'probably', 'actually', 'really', 'literally',
    'basically', 'definitely', 'exactly', 'honestly', 'seriously',
    'apparently', 'obviously', 'totally', 'completely', 'absolutely',

    # nouns
    'thing', 'things', 'stuff', 'time', 'times', 'day', 'days', 'night',
    'week', 'month', 'year', 'hour', 'minute', 'place', 'way', 'case',
    'point', 'part', 'side', 'end', 'fact', 'life', 'world', 'home',
    'work', 'job', 'people', 'person', 'guy', 'girl', 'man', 'woman',
    'friend', 'friends', 'everyone', 'someone', 'anyone', 'nobody',
    'everything', 'something', 'anything', 'nothing',
    'today', 'tomorrow', 'yesterday', 'morning', 'evening', 'afternoon',
    'money', 'phone', 'office', 'college', 'school', 'class', 'exam',
    'food', 'water', 'sleep', 'movie', 'game', 'song', 'photo', 'pic',
    'plan', 'idea', 'problem', 'issue', 'reason', 'question', 'answer',
    'text', 'chat', 'group', 'link', 'post', 'comment', 'reply',
    'free', 'busy', 'late', 'early', 'soon', 'later', 'online', 'offline',
    'out', 'inside', 'outside', 'near', 'far', 'close', 'open', 'done',
    'buy', 'sell', 'pay', 'cost', 'price', 'order', 'book', 'check',

    # numbers
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',

    # pronouns
    'him', 'them', 'us', 'from', 'into', 'onto', 'upon', 'about', 'after',
    'before', 'between', 'through', 'during', 'under', 'over', 'above', 'below',

    # chat slang
    'lol', 'lmao', 'lmfao', 'rofl', 'haha', 'hehe', 'hihi', 'omg', 'wtf',
    'idk', 'idc', 'idgaf', 'tbh', 'ngl', 'imo', 'imho', 'fyi', 'btw', 'afaik',
    'smh', 'ffs', 'jk', 'irl', 'tho', 'tho', 'rn', 'atm', 'asap',
    'ppl', 'pls', 'plz', 'thx', 'ty', 'np', 'nvm', 'ofc', 'obv',
    'gonna', 'wanna', 'gotta', 'kinda', 'sorta', 'lemme', 'gimme', 'dunno',
    'wat', 'wut', 'abt', 'abt', 'thats', 'whats', 'hows', 'whos',
    'shud', 'cud', 'wud', 'chk', 'pls', 'msg', 'msgs', 'rply',
    'tom', 'tmrw', 'tmr', 'tomo', 'yday', 'ytd', 'yest',
    'summa', 'somn', 'smth', 'smthn', 'sumn', 'alone', 'full', 'half',
    'coz', 'cos', 'cuz', 'bcoz', 'bcuz', 'bcz', 'bc', 'because',
    'dont', 'didnt', 'wont', 'cant', 'shouldnt', 'wouldnt', 'couldnt',
    'isnt', 'arent', 'wasnt', 'werent', 'havent', 'hasnt', 'hadnt',
    'doing', 'eating', 'going', 'coming', 'seeing', 'saying', 'asking',
    'eat', 'ate', 'eaten', 'drink', 'drank', 'drunk', 'play', 'played',
    'room', 'rooms', 'unit', 'units', 'house', 'home', 'hostel', 'floor',
    'ok', 'okay', 'okk', 'okkk', 'okayy', 'okayyy', 'kay', 'kk', 'kkk',
    'yes', 'yea', 'yeah', 'yeahh', 'yess', 'yesss', 'yup', 'yep', 'yeppp',
    'no', 'nah', 'nope', 'noo', 'nooo',
    'hmm', 'hmmm', 'umm', 'ummm', 'uhh', 'uhhh', 'ahh', 'ahhh', 'ohh', 'ohhh',
    'aha', 'oho', 'wow', 'woww', 'woah', 'whoa', 'damn', 'dang', 'darn',
    'bro', 'bruh', 'bruhhh', 'dude', 'man', 'boi', 'boii', 'gal', 'sis',
    'guys', 'yall', 'fam', 'homie', 'bestie', 'babe', 'bby', 'hun',
    'sir', 'mam', 'miss', 'mrs', 'mama', 'papa', 'mom', 'dad',
    'shit', 'crap', 'fuck', 'hell', 'ass', 'bitch', 'wtf', 'wth',
    'cool', 'lit', 'fire', 'sick', 'dope', 'nice', 'noice', 'awesome',
    'super', 'ultra', 'mega', 'hyper', 'extra',
    'love', 'hate', 'like', 'thank', 'thanks', 'sorry', 'please',
    'bye', 'byee', 'byeee', 'cya', 'ttyl', 'gn', 'gm', 'gtg',
    'hii', 'hiii', 'hiiii', 'hey', 'heyy', 'heyyy', 'hello', 'helloo',
    'wya', 'wyd', 'hru', 'hbu', 'sup', 'wassup', 'whatsup',

    # tamil chat words - basic
    'da', 'di', 'na', 'la', 'ha', 'ya', 'ra', 'pa', 'ma', 'va',
    'dei', 'dai', 'dey', 'ada', 'adi', 'illa', 'enna', 'epdi', 'enga',
    'seri', 'sari', 'ok', 'hmm', 'aama', 'aana', 'appo', 'ippo',
    'nee', 'naan', 'avan', 'aval', 'anga', 'inga', 'thaan', 'dhaan',
    'kandipa', 'paru', 'sollu', 'sollren', 'sollura', 'pannren', 'pannura',

    # tamil - pronouns & demonstratives
    'naa', 'naanu', 'naan', 'naanga', 'naangal',
    'nee', 'nenga', 'neenga', 'ningal', 'nin', 'unga', 'ungal',
    'avan', 'aval', 'avanga', 'avangal', 'ava', 'ivan', 'ival', 'ivanga',
    'athu', 'adhu', 'ithu', 'idhu', 'atha', 'itha', 'adha', 'idha',
    'antha', 'andha', 'intha', 'indha', 'etha', 'edha', 'entha', 'endha',
    'athaan', 'adhaan', 'ithaan', 'idhaan', 'athey', 'adhey', 'ithey', 'idhey',
    'athaane', 'adhaane', 'athaana', 'adhaana',
    'athanda', 'thanda', 'thonda', 'athonda',
    'athuvum', 'ithuvum', 'athuve', 'ithuve',
    'enn', 'unn', 'ennoda', 'unnoda', 'ennaku', 'enakku', 'unakku', 'onnaku',

    # tamil - verbs (be/is/are variations)
    'iruku', 'irukku', 'irukkum', 'iruka', 'irukka', 'irukkaathu',
    'iruken', 'irukken', 'irukom', 'irukkurom', 'irukanga', 'irukkanga',
    'irundha', 'irundhu', 'irundhaal', 'irundhuchu', 'irunduchu', 'irunthichu',
    'irukkaan', 'irukkaa', 'irukaan', 'irukka', 'irukaan',
    'irruku', 'irrukku', 'irrukum', 'irruka', 'irrukka',
    'illa', 'illai', 'illaiya', 'illaye', 'ille', 'illiya',
    'illaye', 'illadha', 'illaadha',
    'airuchu', 'achu', 'aachu', 'ayiduchu', 'aiduchu',

    # tamil - verbs (common actions)
    'panna', 'pannu', 'pannunga', 'pannuren', 'pannuven', 'pannurom',
    'pannudhu', 'pannuchu', 'panniruken', 'panniruka', 'pannalam', 'panlaam',
    'sollu', 'solla', 'sollren', 'sollunga', 'sollura', 'sonnen', 'sonna',
    'solradhu', 'solraanga', 'solranga', 'sollurom', 'solluvom',
    'paru', 'paaru', 'paaren', 'paarunga', 'paakuren', 'paakurom',
    'paathuten', 'paathen', 'paathom', 'paarkalaam', 'paakalam',
    'vaa', 'vaanga', 'varen', 'varom', 'vanthuten', 'vanthen', 'vandhutten',
    'varuvom', 'varuvanga', 'varuvaanga', 'vandha', 'vantha',
    'poren', 'porom', 'pona', 'poyiten', 'poiten', 'poiduven',
    'pogalaam', 'polaam', 'povom', 'povaanga',
    'kudukuren', 'kudukkuren', 'kuduthuten', 'kuduthen',
    'edukuren', 'edukkuren', 'eduthuten', 'eduthen',
    'theriyum', 'theriyala', 'theriyathu', 'therla', 'therlaye', 'theriyaadhu',
    'puriyu', 'puriyala', 'puriyum', 'puriyuthu', 'purinjuchu',
    'venum', 'vendum', 'venaam', 'vendaam', 'venumna',
    'mudiyum', 'mudiyala', 'mudiyathu', 'mudinja', 'mudiyaadhu',
    'nenaikuren', 'nenaikkuren', 'nenachen', 'nanaichen', 'nenaippen',

    # tamil - particles & connectors
    'dhan', 'dhaan', 'thaan', 'than', 'thaana', 'dhaana', 'thane', 'dhane', 'dhanae',
    'lam', 'laam', 'ellam', 'elam', 'ellaam', 'elaam', 'elamey', 'ellamae', 'ellame',
    'la', 'lla', 'le', 'ley', 'laye', 'lay', 'lae',
    'um', 'yum', 'kum', 'kkum',
    'kuda', 'kooda', 'koodave', 'kudave',
    'mattum', 'mathum', 'mattumey', 'mathumdhan',
    'thanda', 'dhanda', 'thonda',
    'nu', 'nnu', 'ngaradhu', 'ngardhu',
    'aana', 'aanaa', 'ana', 'aanal',
    'adhaan', 'athan', 'athaan', 'ithan', 'ithaan',

    # tamil - question words
    'enna', 'yenna', 'ennada', 'enada', 'ennadi', 'ennanga',
    'yaar', 'yaaru', 'yar', 'yaara', 'yaaruku',
    'enga', 'yenga', 'engada', 'engadhi', 'engayo',
    'epdi', 'eppadi', 'yeppadi', 'yepdi', 'eppudi', 'yeppudi', 'appudi', 'ippudi',
    'ethu', 'yethu', 'edhu', 'yedhu',
    'yen', 'en', 'yenda', 'enda', 'yenada', 'enada',
    'evolo', 'evlo', 'evalo', 'evlov', 'avlo', 'avolo', 'avlov',

    # tamil - time words
    'ipo', 'ippo', 'ippove', 'ippothan', 'ippodhan', 'ipodhaiku',
    'apo', 'appo', 'appove', 'aprom', 'approm', 'apram', 'aprm',
    'aparom', 'aparam', 'kaprom', 'kapprm', 'kapprom',
    'inniki', 'inniku', 'innaiku', 'indhaiku',
    'naalaiku', 'naalaikku', 'naalaku', 'nalaikku',
    'anniku', 'andhaiku', 'andra', 'andha',
    'munnadhi', 'munnadi', 'appuram', 'apurom',

    # tamil - adjectives & adverbs
    'nalla', 'nallave', 'nallaa', 'nallavan', 'nalladhu',
    'romba', 'rombha', 'romba', 'rombave',
    'konjam', 'konjum', 'koncham', 'konchum',
    'neraiya', 'neraya', 'naraya',
    'sema', 'semma', 'semaya', 'semmaya',
    'periya', 'peria', 'perusa', 'perusu',
    'chinna', 'china', 'chinnadhu', 'chinadhu',
    'pudhu', 'pudhusu', 'pudhusa',
    'pazhaya', 'pazhaiya', 'pazhadhu',

    # tamil - misc common words
    'poru', 'porum', 'pothum', 'podhum',
    'suma', 'summa', 'summave', 'summadhan',
    'vera', 'vere', 'veradhu', 'vereyadhu',
    'ore', 'oru', 'onnu', 'onna', 'orey', 'orey',
    'rendu', 'rendum', 'rendume',
    'moonu', 'monum', 'moonum',
    'naalu', 'naalum', 'naalume',
    'anju', 'anjum', 'anjume',
    'daamn', 'damm', 'damn',
    'ahm', 'uhm', 'hmm', 'hmmm',
    'yeh', 'yehh', 'ehh', 'ehhh',
    'okie', 'okiee', 'oki',
    'gotha', 'kotha', 'goathaa',
    'trw', 'tmw', 'tmrw', 'tomo',
    'nyt', 'nite', 'night',
    'pls', 'plis', 'plss',
    'ohoh', 'oho', 'ohoo',
    'mari', 'maari', 'madri', 'madhiri', 'maadhiri', 'maathiri',
    'thiruppi', 'thirumbi', 'thirupa',
    'ade', 'adey', 'ada', 'aada',
    'polaye', 'polayae', 'pola',
    'moss', 'mosu', 'mossu',
    'tru', 'thru', 'true',
    'mothu', 'modhu', 'motham',
    'adhellam', 'athellam', 'adhalam', 'idhellam', 'ithellam',
    'elaarum', 'ellaarum', 'elarum', 'ellarum',
    'varikum', 'varikkum', 'varkum',
    'solranga', 'solraanga', 'solranunga',
    'ipolam', 'ipolaam', 'ipalam',
    'asaiya', 'aasaiya', 'aasa',
    'dhidirnu', 'thidirnu', 'thideer',

    # generic
    'mean', 'means', 'meant', 'meaning', 'type', 'types', 'kind', 'kinds',
    'sort', 'sorts', 'form', 'forms', 'level', 'levels', 'part', 'parts',

    # contraction leftovers
    'don', 'didn', 'won', 'wouldn', 'couldn', 'shouldn', 'isn', 'aren',
    'wasn', 'weren', 'hasn', 'haven', 'hadn', 'doesn', 'ain',
    'll', 've', 're', 'nt', 'em', 'ill', 'ull', 'yall',

    # time stuff
    'mins', 'min', 'hrs', 'secs', 'sec', 'hour', 'hours', 'minute', 'minutes',
    'second', 'seconds', 'week', 'weeks', 'month', 'months', 'year', 'years',
    'daily', 'weekly', 'monthly', 'yearly', 'ago', 'later', 'soon',

    # activities
    'watch', 'watched', 'watching', 'listen', 'listened', 'listening',
    'dinner', 'lunch', 'breakfast', 'snack', 'snacks', 'brunch',

    # wa/system
    'message', 'messages', 'edited', 'deleted', 'omitted', 'media',
    'image', 'video', 'audio', 'sticker', 'gif', 'document', 'contact',
    'https', 'http', 'www', 'com', 'org', 'net', 'meta', 'whatsapp',
}

# extra stop words for topics only - keep these in personal stats tho
TOPIC_ONLY_STOP_WORDS = CHAT_STOP_WORDS | {
    # tamil slang - fun in personal but not topics
    'poda', 'podi', 'poda', 'poyi', 'po', 'vada', 'vadi',
    'da', 'dei', 'di', 'dey', 'ra', 'ri',
    'aiyo', 'aiyoo', 'aiyyoo', 'chee', 'chi', 'cha',
    'machaan', 'macha', 'machan', 'thala', 'anna', 'akka',
    'enna', 'ethu', 'yaaru', 'yaar', 'yen', 'enga', 'epdi', 'eppadi',

    # tamil filler/grammar words - not meaningful as topics
    'dhan', 'thaan', 'dhaan', 'than', 'thaana',
    'lam', 'ellam', 'elam', 'la', 'lla', 'le', 'ley',
    'oru', 'onnu', 'onna', 'ore',
    'iruku', 'irukku', 'irukkum', 'iruka', 'irukka', 'illa', 'illai',
    'maari', 'maathiri', 'mari', 'madhiri', 'maadhiri',
    'adhu', 'athu', 'idhu', 'ithu', 'andha', 'antha', 'indha', 'intha',
    'ipo', 'ippo', 'apo', 'appo', 'aprom', 'approm', 'apram',
    'panna', 'pannu', 'pannunga', 'pannuren', 'pannuven',
    'sollu', 'solra', 'solla', 'sollren', 'sonnen', 'sonna',
    'paru', 'paaru', 'paaren', 'paarunga',
    'vaa', 'vaanga', 'varen', 'vandhuten', 'vanthen',
    'poren', 'porom', 'pona', 'poyiten',
    'theru', 'therla', 'theriyum', 'theriyala', 'theriyathu',
    'venum', 'vendum', 'venaam', 'vendaam',
    'mudiyum', 'mudiyala', 'mudiyathu',
    'aana', 'aanaa', 'ana', 'but',
    'konjam', 'romba', 'nalla', 'nallave',
    'enna', 'yenna', 'yen', 'yen',
    'enga', 'yenga', 'inge', 'ange',
    'epdi', 'eppadi', 'yeppadi', 'yepdi',
    'yaru', 'yaaru', 'yar',
    'inga', 'anga', 'enga',
    'innum', 'innu', 'inniki', 'naalaiku', 'naalaikku',
    'rendu', 'moonu', 'naalu', 'anju',
    'than', 'thana', 'nu', 'nnu', 'aam', 'aama',
    'kuda', 'kooda', 'um', 'yum',
    'poo', 'pooo', 'va', 'vaa',

    # common expressions
    'bro', 'bruh', 'dude', 'man', 'guys',
    'sad', 'happy', 'nice', 'cool', 'lol', 'haha',
}
