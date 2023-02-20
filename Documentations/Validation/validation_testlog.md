# Test the negative output for validation:

## Aim: Take a wrong logic model in Arena (more machines, different queues capacities) and wrong input (different distributions) and test the validation.

## Steps:
I can give more instructions about how to run the digital twin, but should be straight forward right now that it's working properly.

You just need to save the data from real world (Arena) in a database .db with the name like "real_"+ "<digital twin name>" inside of the folder databases.

You should create a digital twin object like this my_DT = Digital_Twin(name= "<digital twin name>", initial = True, until= 200100). In this case we are testing the 5s model, so to keep using the same model from the other test the name should be "5s_mode_distribution" (something like that, check the model inside of the folder "models").

After that you run a normal simulation, my_DT.run_digital_model() and than run the simulation my_DT.run_validation()

## Test conditions and results:
1. preliminary test was done with existing data which we know gives a good results.
- LCSS:TDS=1.0; LCSS:qTDS=0.9967.
- Abscence of station 3 and queue2 verified. therefore: test procedure is valid.

2. actual test is done by changing the queue capacity of queue1 to 1 and reducing station 1 processing to norm(1000,100) to force parts through queue2 in real system (5s_Model_Tracelog_alt1).
- LCSS:TDS 0.7126760563380282; LCSS:dTDS 0.8950819672131147.
- digital model couldnt redirect parts to queue2 and station3 as the queue1 capacity is 10 which was still high.
- Reduction in LCSS:TDS and LCSS:qTDS shows that the validation program can recognize the differences.

3. additional test[1] to force parts through station 3 in digital model. For this, digital model was changed (queue1 capacity: 10 --> 1). Real data of actual test is maintained.
- LCSS:TDS 0.2057142857142857; LCSS:qTDS 0.8950819672131147.
- Now digital model starts involving station 3 for processing.
- LCSS:TDS value comparison with actual test looks odd or unnatural as this one is lower than the actual test. Because, actual test didnt have station 3 at all when compared to the real data, meanwhile this test had included station 3 which is more closer to the actual logic of the system. Which means, the LCSS:TDS value which shows the accuracy of logic/layout should have increased.
- LCSS:qTDS looks impressive as it returned the exact same value as before. This could be because, there was no difference in the processing distributions of the stations between real and digital model.
- test was rerun for verification and similar output was obtained

4. additional test[2] is done by changing station 1 distribution to match real system (station1: norm(5000,500) --> norm(1000,100)).
- LCSS:TDS 0.20454545454545456; LCSS:qTDS 0.8126801152737753
- LCSS:TDS remains in the lower zone as previous zone. might be indicating, digital model followed a different trace compared to real system. This could be an issue as the real and digital system parameters are same just like the preliminary test did in the beginning. Main difference is the involvement of queue3 and station3 which is a source of parts rearrangement in the system which can create a error propogation.
- LCSS:qTDS does also saw a reduction which shouldnt have happened.

5. additional test[3] is done by reverting queue1 capacity (queue1 capacity: 1 --> 10). Real data is same.
- LCSS:TDS 0.7126760563380282; LCSS:qTDS 0.8097982708933718
- no trace of queue2 or station 3

6. additional test [4] is done by reverting all the changes did to the digital model. All the old changes to the real system are also reverted. To check the influence of queue2, a new change is made in the real system (station 5 processing: norm(2000,200) --> norm(8000,200)) (5s_Model_Tracelog_alt2). We are expecting a good LCSS:TDS value as the change is in the end of the system.
- LCSS:TDS 1.0; LCSS:qTDS 0.8870292887029289
- as expected LCSS:TDS is perfect but LCSS:qTDS is lower than 0.9.

We can conclude that the vaildation codes are good and running. They are capable of finding the differences in logic and input validation. Further investigation has to be made into why the cases with Queue2 & station3 involved couldn't be vaildated in terms of logic when there is an invalid input validation.