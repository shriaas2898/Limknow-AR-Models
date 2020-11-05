import sys, json, datetime, requests
from collections import OrderedDict
from operator import getitem
from re import search
from github import Github

'''
Takes existing data of JSON file, username and PR information as input and adds a record to the JSON file
and returns the data of updated JSON file.
'''
def add_record(data,username,pr_dict):
    
    # Add new record or update existing record
    data[username] = {"count": len(pr_dict),
                      "contributions": pr_dict
                    }
    # Sort records in reverse order
    data = OrderedDict(sorted(data.items(), 
                    key = lambda x: getitem(x[1], 'count'),reverse=True))
    # Write sorted records in JSON file
    with open("community-contributions.json","w") as write_file:
            json.dump(data,write_file,indent=2)
    return data



'''
Updates the leaderboard
'''

def update_leaderboard(data,start_marker,end_marker,file_name):

    with open(file_name,"r") as read_file:
        read_data = read_file.readlines()
        # Get index of starting of leaderboard records
        start = (read_data).index(start_marker) + 2 # line after table header
        # Get index of ending of leaderboard records
        end = (read_data).index(end_marker) + 2 # line after end of table
        write_data =  "".join(read_data[:start])
        
    # Updating leaderboard from JSON file data
    # An empty list to store all the records
    records= []
    # Building string for record 
    for usr,info in data.items():
        records.append(f"| [@{usr}](https://github.io/{usr}) | {info['count']} | <details> <summary>List of Contributions </summary>")
        for link, pr in info["contributions"].items():
            records.append(f" - [{pr}]({link}) <br>")
        records.append("</details> |\n")
    
    # Combining all the records in a final string
    write_data =  write_data+"".join(records)+end_marker
    write_data = write_data+"".join(read_data[end:])

    # Writing on README file
    with open(file_name,"w") as write_file:
        write_file.write(write_data)


if __name__ == "__main__":
    # try:
        
        pr_id = sys.argv[1].strip()
        print("id  = ",pr_id)
        g = Github()
        repo = g.get_repo("shriaas2898/Limknow-AR-Models")
        pr = repo.get_pull(int(pr_id))

        # Getting label names for the PR
        labels = [x.name for x in pr.get_labels()]

        # Check if PR has `New Model` label and the status is `merged`
        if(('New Model' not in labels) or (pr.is_merged() == False)):
            print("PR invalid! Ciao!")
            exit()
        # Get records from JSON file
        with open("community-contributions.json","r") as read_file:
            contr_data = json.load(read_file)

        # Create a dictionary
        pr_dict = {}
    
        # Adding PR to the dictionary
        link = pr.html_url
        title = pr.title
        pr_dict[link] = title
    
        username = pr.user.login
        # For adding new record 
        contr_data = add_record(contr_data,username,pr_dict)
        
        # Update the leader board
        update_leaderboard(contr_data, '| Name | Number of Contributions | Link of Contribution|\n', '<!-- End of Leaderbaord-->\n', 'README.md')        
        
        print("Successfully added your contribution")
    
    # except LeaderbaordError as e:
    #     print(str(e))
    # except Exception as e:
    #     print("Internal error occured. Please try again later.")
