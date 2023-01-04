# Scopus-Notion Query Result exchange

## Overview

Following content explains how to download and upload query results obtained from Scopus to research database in Notion. The topics available from the query are:
- **Title** - will be entered as **Name** in the database
- **Document type** - will be entered as **Material type** in the database
- **Link**
- **Author Keywords, Index Keywords** - will be merged as **************Keyword**************
- **Affiliation** - will be as entered as Country
- **Year**- year
- **Abstract**

**Type** column to be entered with **Academic** as the content manually in the .csv file.

## Steps

1. Download the query result by selecting the following options:

![image](https://user-images.githubusercontent.com/114431364/210454273-8cceeaa5-cc39-45bf-ab2c-067b6a655c63.png)

2. Query results are downloaded as .csv file.
3. Do the following steps inside the csv file to match the headers in the Notion database:
    1. Rename **Title** column as **Name.**
    2. Add a new column between 1st and 2nd column named **Type**.
    3. Enter type as **Academic**. Use **shift+<double tap at corner of the cell>**  to copy the value till the end of the table. (Alternate way to fill by drag).
    4. Rename Document Type as **Material Type**.
    5. Find and replace "**;**" with "**,**". This is for Notion to recognize tags.
    6. Create a new column **Keyword**.
    7. Merge **Author Keyword** and **Index keyword** columns to **Keyword** column using **=concat(<cell1>,",",<cell2>")**. Copy the formula till the end of the column. **Copy** and **Paste: Values** in the same column to remove the concat() formula dependency to **Index keyword** and **Author keyword** column. This allows to delete the two columns without formula error.
    8. Rename **Affiliation** column as **Country**.
    9. Delete the unnecessary remaining columns like **Source**, **Index keyword** and **Author keyword**.
    10. Don’t forget to click Save.
    
    Above steps could be automated, at least partially, using excel macros. Follow the instructions given in the support page of Microsoft below to record and run macros:
  [https://support.microsoft.com/en-us/office/automate-tasks-with-the-macro-recorder-974ef220-f716-4e01-b015-3ea70e64937b](https://support.microsoft.com/en-us/office/automate-tasks-with-the-macro-recorder-974ef220-f716-4e01-b015-3ea70e64937b)
 
