from dtwinpylib.dtwinpy.tester import Tester
test = tester()

#--- create allexp databse
# test.create_allexp_database()

test = Tester()
test.initiate()

print(f"'{test.exp_id}' experiment is loaded")