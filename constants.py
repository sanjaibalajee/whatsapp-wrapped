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

# bots etc
IGNORED_SENDERS = [
    "Meta AI",
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

    # tamil chat words
    'da', 'di', 'na', 'la', 'ha', 'ya', 'ra', 'pa', 'ma', 'va',
    'dei', 'dai', 'dey', 'ada', 'adi', 'illa', 'enna', 'epdi', 'enga',
    'seri', 'sari', 'ok', 'hmm', 'aama', 'aana', 'appo', 'ippo',
    'nee', 'naan', 'avan', 'aval', 'anga', 'inga', 'thaan', 'dhaan',
    'kandipa', 'paru', 'sollu', 'sollren', 'sollura', 'pannren', 'pannura',

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
    # common expressions
    'bro', 'bruh', 'dude', 'man', 'guys',
    'sad', 'happy', 'nice', 'cool', 'lol', 'haha',
}
