from nltk.corpus import words
import Levenshtein


class ClusterDataframe:

    def __init__(self, df):
        self.df = df
        self.place_holder_list = ['_','-','*','~','/']
        self.word_set = set(words.words())

    def setdf(self):


        self.df['location'] = self.df.apply(self.locate_pert,axis=1)
        # grouped_multiple['distance'] = grouped_multiple.apply(distance,axis=1)
        self.df['pert_word'] = self.df.apply(self.show_pert,axis=1)
        self.df['is_special'] = self.df.apply(self.classify_perturbation_type, args=(self.special_character,), axis=1)
        self.df['is_repeat'] = self.df.apply(self.classify_perturbation_type, args=(self.repeat_char,), axis=1)
        self.df['is_interesting_up'] = self.df.apply(self.classify_perturbation_type, args=(self.interesting_lowercase_uppercase,), axis=1)
        self.df['is_up'] = self.df.apply(self.classify_perturbation_type, args=(self.lowercase_uppercase,), axis=1)
        self.df['is_abbr'] = self.df.apply(self.classify_perturbation_type, args=(self.abbr,), axis=1)

        # print(grouped_multiple[grouped_multiple["is_special"] == 1].shape)
        # print(grouped_multiple[grouped_multiple["is_repeat"] == 1].shape)
        # print(grouped_multiple[grouped_multiple["is_interesting_up"] == 1].shape)
        # print(grouped_multiple[grouped_multiple["is_up"] == 1].shape)
        # print(grouped_multiple[grouped_multiple["is_abbr"] == 1].shape)


    def classify_perturbation_type(self, row, func):
        c,p = row['clean_version'].split()[row['location']], row['pert_word']
        return 1 if func(c,p) else 0



    def locate_pert(self, row):
        # print(row)
        c,p = row['clean_version'].split(), row['perturbed_version'].split()
        for i in range(len(c)):
            if c[i] != p[i]:
                return i
        return -1


    def distance(self, row):
        l = row['location']
        c,p = row['clean_version'].split()[l], row['perturbed_version'].split()[l]
        return Levenshtein.distance(c.lower(),p.lower())


    def show_pert(self, row):
        l = row['location']
        return row['perturbed_version'].split()[l]


    def simplify_word(self, word):
        pw = list(word.lower())
        i = 1
        while i < len(pw):
            if pw[i] == pw[i-1]:
                pw.pop(i)
            else:
                i += 1
        return ''.join(pw)


    def lowercase_uppercase(self, clean_word, pert_word):
        return pert_word[1:].lower() != pert_word[1:] and pert_word.upper() != pert_word


    def interesting_lowercase_uppercase(self, clean_word, pert_word):
        collect = ''
        for c in pert_word:
            if c.lower() != c:
                collect += c
        return pert_word.lower() != pert_word and collect.lower() in self.word_set and len(collect) != len(pert_word) and len(collect) > 1


    def repeat_char(self, clean_word, pert_word):
        c,p = clean_word.lower(),pert_word.lower()
        simp_c, simp_p = self.simplify_word(c), self.simplify_word(p)
        return len(p) > len(c) and simp_c == simp_p and simp_p != p


    def abbr(self, clean_word, pert_word):
        c,p = clean_word.lower(),pert_word.lower()
        i = 0
        for character in c:
            if character == p[i]:
                i += 1
                if i == len(p):
                    return len(p) < len(c)
        return False


    def placeholder(self, clean_word, pert_word):
        if len(pert_word) < 4:
            return False
        for c in list(pert_word):
            if c in self.place_holder_list:
                return True
        return False


    def special_character(self, clean_word, pert_word):
        for c in list(pert_word.lower()):
            if (c < 'a' or c > 'z') and c not in self.place_holder_list:
                return True
        return False

