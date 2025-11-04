# class textClass:
#     test_var = 'Hello'
#     another_var = (1,2,3,4)

#     def test_func(self):
#         print('from the function')
#         print(self.test_var)
#         self.another_func('123')

#     def another_func(self, test_param):
#         print(test_param)


# test = textClass()
# test.another_var = 'new value'
# print(textClass.another_var)

# print(textClass.test_var)

# test2 = textClass()
# test2.test_func()
# test2.another_func('hehe boi')


class Mage:
    def __init__(self, health, mana):
        self.health = health
        self.mana = mana
        print("mage class created")
        print(self.health)
        print(self.mana)

    def __len__(self):
        return self.mana

mage = Mage(100, 200)
print(len(mage))