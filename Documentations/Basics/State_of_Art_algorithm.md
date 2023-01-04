# Collection of Academic Articles
- The articles belonging to **Academic** type for the State-of-Art were collected online from **Scopus**.
- Following keywords were used to make the query in Scopus.
```python
( TITLE ( "digital twin" )
AND
ALL ( "manufacturing" OR "production" )
AND
ALL ( applications OR "discrete event simulation" OR "process mining" OR "model generation" OR sustainability OR types OR categories OR architecture OR framework OR standards ) )
```
- A total of 3507 papers were collected as a result of the search query. The Article Title, Document Type, Affiliation, Year, Keywords and Abstract were downloaded as .CSV file.

# Pre-Processing

note: The following algorithmic description would not be recommend to be used for a low amount of papers, since a manual selection would be more trustworthy, but it can be useful when dealing with a high amount of content and could be use for a first selection criteria. 

 

1. The downloaded .csv file was fed to an python based algorithm which clustered the papers based on the keywords (stemmed keywords). The algorithm clustered the **3507** articles into **460 clusters.**
2. In order to cluster the papers, some python libraries and consolidated methods were used. The main packages are: 
    
    2.1 nltk(Natural Language Tool Kit)
    
    2.2 sklearn (Machine Learn library)
    
    ```python
    from nltk.stem import PorterStemmer
    from nltk.corpus import stopwords
    
    from sklearn.feature_extraction.text import TfidfVectorizer #convert text to matrix number
    from sklearn import cluster #group keywords
    ```
    
3. Using theses libraries, the following steps were use:
    
    3.1 Definition of a tokenizer
        3.1.1 transform words into its root so you reduce the number of different combinations for the same word
        - Example: Builder, Building, etc → Build
        3.1.2 Define stop-words to not consider secondary words
        - Example: not, to, of, the, was, are, etc
        - In this case, “Digital Twin” was add as a stop-word since all the papers has this words.
    
    3.2 Vectorize the data (transform the set of keywords in a vector). The following table makes it clear:
    
    |  | A | B | C | D | E | F | G | H | M | N |
    | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    | A, B, D, E | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
    | A, C, F, M,  | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
    | B, E, G, N | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 1 |
    | H, C, F, M | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 |
    
    3.3 With this *DataFrame,* we can use *Affinity Propagation* to make the clustering.
    
    3.4 The following image shows the number of papers per cluster:
        ![image](https://user-images.githubusercontent.com/114431364/210458950-16387f81-d856-4e64-b31c-3559bb4c81df.png)
    

4. To remove irrelevant clusters, scores were provided for each cluster based on cluster keywords and priority keywords.
    + The following keywords were used as priority keywords as they were more relevant than other keywords (main keywords):
        - manufacturing
        - pruduction
        - shop floor
        - forecasting
        - model generation process
        - mining
        - sustainability
        - architecture
        - framework
        - discrete event simulation
    + To create the score for each cluster, the algorithmic count the number of times that any of the main keywords appears in the set of the cluster’s keywords
    + The next image shows this counting for each cluster

      ![image](https://user-images.githubusercontent.com/114431364/210460220-915cd4ac-e25b-411e-a976-bf57206eaf14.png)

    + The score is given by the percentage rate between the counting and the total number of keywords for each cluster

    +  Based on the score, following scatter plot was plotted:

        ![image](https://user-images.githubusercontent.com/114431364/210460238-f6293d46-9b4c-40b3-bc4f-8731569c10c0.png)

    + A threshold of **0.15** was selected (red line). The clusters above this critical threshold was accepted as they have relevancy of more than **15%**. After this, **55 clusters** with **587 papers** were accepted.

5. To further scrutinize the list of articles, a selection of papers were done inside the clusters based on the same keywords comparison.
    + So, within the selected clusters, the algorithms counts the number of times that any of the main keywords appears in the papers (counter). The counter for each paper is shown in the next image:

      ![image](https://user-images.githubusercontent.com/114431364/210460534-342d4e5a-0da4-40b4-b370-7dd46459613f.png)

    + Taking the percentage between the counter and the total number of keywords for each paper you have the individual score, as the next image shows:

      ![image](https://user-images.githubusercontent.com/114431364/210460596-7651d1ff-58af-477e-89d2-e7335540d1c5.png)

    + A threshold value of **0.2** was used to select papers with more than **20%** relevancy. After the selection process, a total of **223 articles** were shortlisted and exported as .CSV file for further review.

# Processing (manually)

The **223 articles** shortlisted would be reviewed **manually** by reading the article title, year and abstract. Following criteria with weightage is used to score the articles:

| Criteria | Weightage | Score range |
| --- | --- | --- |
| Digital twin quality (DTQ) | 20% | 1 - Complete definition; 0.5 - incomplete development; 0 - wrong definition |
| Application/Area (AA) | 20% | 1 - related to manufacturing/production; 0 - others |
| Single or Multiple  Machines/Assets (SM) | 16% | 1 - Multiple asset/ system level DT; 0 - Single asset/ individual machine level DT |
| Specific DT or Generic DT (SG) | 16% | 1 - Generic application/scenario; 0 - Specific application/scenario |
| Year (Y) | 14% | 1 - year ≥2021; 0 - year <2021 |
| New or existing Methods/Tools (NM) | 14% | 1 - New/Unknown; 0 - Existing/Known |

So finally manually score for each paper is given by the following formula:

$Score = 0,2 . DQT + 0,2 . AA + 0,16 . SM + 0,16 . SG + 0,14 . Y + 0,14 . NM$

With this score we are going to be able to select the most relevant paper for reading and update the list of main keywords for further researches.
