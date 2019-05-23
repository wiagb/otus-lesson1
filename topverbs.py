import ast
import os
import collections

from nltk import pos_tag


def flat(list_of_tuple):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in list_of_tuple], [])


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return  pos_info[0][1] == 'VB'


#Функция получает путь для поиска .py файлов
#Для каждого файла строит AST и возвращает список всех AST
def get_trees(path):
    filenames = []
    trees = []
    #Получение списка полных путей к файлам *.py
    for dirname, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                filenames.append(os.path.join(dirname, file))
    print('total %s files' % len(filenames))
    # Открытие файла Python
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        #получение абстрактного синтактического дерева
        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None
        trees.append(tree)
    print('trees generated')
    return trees




#Функция получает имя функции
#Ищет в имени части текста, разделенные _ и если эта часть имени-глагол
#Возвращает список частей глаголов
def get_verbs_from_function_name(function_name):
    return [word for word in function_name.split('_') if is_verb(word)]


# Функция принимает список абстракных синтаксических деревьев
# Возвращает список имен всех функций, за исключением "магических" __имя__
def get_functions_name(trees):
    # Для каждого py файла получаем списки имен функций
    list_of_functions_name = [[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in
                              trees]
    # Переводим списки имен функций разных файлов в единый список
    all_functions_name = flat(list_of_functions_name)
    # Исключаем "магические" функции
    return [f for f in all_functions_name if not (f.startswith('__') and f.endswith('__'))]



#Функция принимает список директорий
#Рекурсивно ищет в директориях файлы *.py
#Возвращает список встречаемых глаголов в названии функций в найденных Python файлах
def get_verbs_in_dirs(dir_list):
    verbs = []
    for directory in dir_list:
        path = os.path.join('.', directory)
        # получение списка абстрактных синтактических деревьев для каждого py файла
        trees = [t for t in get_trees(path) if t]
        all_functions = get_functions_name(trees)
        print('functions extracted')
        # Получение списка глаголов
        verbs += flat([get_verbs_from_function_name(function_name) for function_name in all_functions])
    return verbs

#Функция принимает список глаголов, количество глаголов, которое необходимо вывести на печать
#Выводит на печать популярные глаголы и количество их вхождений
def show_n_topverbs(verbs, top_size):
    print('total %s words, %s unique' % (len(verbs), len(set(verbs))))
    for word, occurence in collections.Counter(verbs).most_common(top_size):
        print(word, occurence)




if __name__=='__main__':
    #директории, в которых будем искать
    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
    ]
    verbs=[]
    #Получаем список наиболее часто встречающихся глаголов
    verbs=get_verbs_in_dirs(projects)
    #Показываем первые top_size глаголов
    top_size = 10
    show_n_topverbs(verbs, top_size)
