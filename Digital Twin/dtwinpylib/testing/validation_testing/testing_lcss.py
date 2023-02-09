def LCSSR(vector1, vector2, delta_t, eps = None, order = False, seq_string = False):
    flag_str = False
    if type(vector1[0][0]) == str and seq_string == False:
        flag_str = True
        eps = 0
        for i in range(len(vector1)):
            vector1[i][0] = ord(vector1[i][0])

        for j in range(len(vector2)):
            vector2[j][0] = ord(vector2[j][0])

    if seq_string == True:
        #### MaquinaID_Status_PartID ####
        # MaquinaID = str 1 to 9
        # Status = 1 (started) or 0 (finished)
        # Part ID = the rest of the string
        # M1 started P15: 1115

        for i in range(len(vector1)):
            for j in range(len(vector1[i][0])):
                if vector1[i][0][j] == "s": vector1[i][0][j] = "1"

                elif vector1[i][0][j] == "f": vector1[i][0][j] = "0"

            vector1[i][0] = int(vector1[i][0])

        for i in range(len(vector2)):
            for j in range(len(vector2[i][0])):
                if vector2[i][0][j] == "s": vector2[i][0][j] = "1"

                elif vector2[i][0][j] == "f": vector2[i][0][j] = "0"
            
            vector2[i][0] = int(vector2[i][0])

        print(f"vector1: {vector1}")
        print(f"vector2: {vector2}")
            

        


    # initialize the lengths of the two input vectors
    m, n = len(vector1), len(vector2)
    
    # create a 2D dp array with m+1 rows and n+1 columns,
    # where each cell stores the length of the longest common sub-sequence between 
    # the prefixes of the two input vectors
    dp = [[0 for j in range(n + 1)] for i in range(m + 1)]
    
    # initialize an empty list to store the events that belong to the longest common sub-sequence
    lcss = []
    jstart = 1
    # loop through each event in vector1
    for i in range(1, m + 1):
        # loop through each event in vector2
        for j in range(jstart, n + 1):
            # check if the current events in vector1 and vector2 are within the eps and delta_t threshold,
            # and if the time difference between them is less than or equal to delta_t
            if abs(vector1[i-1][0] - vector2[j-1][0]) <= eps and abs(vector1[i-1][1] - vector2[j-1][1]) <= delta_t:
                # if the current events match, update the dp cell with the value from the previous cell + 1
                dp[i][j] = dp[i-1][j-1] + 1
                # add the current event from vector1 to the lcss list
                lcss.append(vector1[i-1])

                #--- Mark the j used, the next iteration will look from this j to forward
                if order == True:
                    jstart = j

                # break from the inner loop
                break
            else:
                # if the events don't match, update the dp cell with the max value from the previous cells
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    #--- Similarity Indicator
    indicator = len(lcss) / min(m,n)


    #--- If it was a string, convert it back to string
    if flag_str == True:
        for i in range(len(lcss)):
            lcss[i][0] = chr(lcss[i][0])

    # return the longest common sub-sequence
    return lcss, indicator



S1 = [[1, 1], [5,2], [7, 3], [4, 4], [3, 5], [8, 6]]
S2 = [[1, 1], [4, 2], [7, 3], [6, 4], [5, 5]]

(lcss_list, indicator) = LCSSR(S2, S1, delta_t= 1, eps= 1, order= True)
print (f"LCSS LIST: {lcss_list}")
print(f"Indicator: {indicator}")


