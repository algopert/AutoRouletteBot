# # from pathlib import Path
# # Path("./directory").mkdir(parents=True, exist_ok=True)

# import xml.etree.ElementTree as ET

# conditions = {}

# def read_conditions():
#     global conditions
#     myXMLtree = ET.parse('params_config.xml')
    
#     _gameMode = myXMLtree.find('gameMode').text
#     if 'BACKTEST' in _gameMode:
#         gameMode = 'BACKTEST'
#     elif 'REALGAME' in _gameMode:
#         gameMode = 'REALGAME'
#     else:
#         gameMode = 'READONLY'
    
#     _outputMode = myXMLtree.find('outputMode').text
#     if 'TELEGRAM' in _outputMode:
#         outputMode = 'TELEGRAM'
#     else:
#         outputMode = 'CONSOLE'
#     ############       Read parameters       ###############    
#     params = myXMLtree.find('Parameters')
#     for child in params:
#         print(child.tag)
#         conditions[child.tag] = {}
#         for item in child:
#             print("\t", item.tag, item.text)
#             conditions[child.tag][item.tag] = int(item.text)
        
        
# read_conditions()

# print(conditions['Age_Of_The_Gods_Bonus_Roulette']['BasePrice'])



# condition_list = {"Red": [0, 1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
#                      "Black": [0, 2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
#                      "Odd": [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35],
#                      "Parity" : [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
#                      "Low" : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
#                      "High" : [0, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36] }

# print(list(condition_list.keys())[0])



x = [4, 27, 31, 36, 4, 7, 23, 35, 30, 20, 26, 18, 0, 3, 25, 2, 14, 7, 3, 27, 30, 8, 33, 5, 31, 25, 29, 34, 0, 30, 36, 17, 14, 11, 35, 9, 36, 12, 32, 27, 13, 29, 26, 2, 6, 22, 32, 22, 12, 22, 35, 9, 22, 27, 36, 2, 15, 19, 35, 2, 27, 36, 6, 3, 24, 21, 12, 36, 22, 34, 2, 10, 11, 10, 16, 17, 22, 9, 34, 17, 23, 0, 6, 18, 9, 32, 33, 36, 23, 26, 8, 13, 35, 9, 0, 35, 25, 8, 5, 24, 11, 31, 9, 14, 13, 8, 14, 32, 26, 21, 22, 8, 5, 31, 13, 9, 3, 0, 8, 33, 26, 34, 9, 34, 20, 15, 0, 10, 23, 14, 32, 33, 24, 11, 6, 33, 2, 30, 6, 4, 36, 27, 8, 18, 8, 9, 22, 1, 35, 8, 26, 36, 36, 5, 6, 27, 26, 4]

y = x[5:15]
print(y)
y.reverse()
print(y)
print(x[5:15])


from random import randrange

print(randrange(10))
print(randrange(10))
print(randrange(10))
print(randrange(10))


print(not None)


    
















