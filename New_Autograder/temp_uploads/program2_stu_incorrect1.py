# -*- coding: utf-8 -*-


# While Loop incorrect in this file



import csv



def main():
    
    contacts = read_contacts()
    
    option = 0
    
    while True:
        
        # display the menu
        menu()
        
        option = int(input('\nEnter your choice: ').strip())
        
        if option == 1:
            add_contact(contacts)
            
        if option == 2:
            view_contacts(contacts)
            
        if option == 3:
            search_contact(contacts)
            
        if option == 4:
            remove_contact(contacts)
            
        if option == 5:
            update_contact(contacts)
            
        if option == 6:
            save_contacts('contacts.csv', contacts)
            
            print('Contacts successfully saved! Program Terminating......')
            break
            
        else:
            print('Invalid option. Please choose a valid option.')



# read contacts from CSV file
def read_contacts():
    
    '''
    reads contacts from a CSV file and returns a list of contacts.

    Returns
    -------
    list
        a list of contacts, where each contact is represented as a dictionary
        with keys corresponding to column names in the CSV file. 
    '''
    contacts = []
    
    try:
        with open('contacts.csv', mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                contacts.append(row)
                
    except FileNotFoundError:
        print('Contacts file NOT found.')
        
    return contacts


# save contacts to CSV file
def save_contacts(filename, contacts):
    
    '''
    saves a list of contacts to a CSV file.

    Parameters
    ----------
    contacts : list of dict
        a list where each dictionary represents a contact with keys 
        corresponding to 'FirstName', 'LastName', 'Phone', and 'Email'.

    Returns
    -------
    None
        
    '''     
    with open('contacts.csv', mode='w', newline='') as file:
        fieldnames = ['FirstName', 'LastName', 'Phone', 'Email']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for contact in contacts:
            writer.writerow(contact)
            
            
# add a new contact
def add_contact(contacts):
    
    '''
    adds a new contact to the list of contacts.

    Parameters
    ----------
    contacts : list of dict
        a list where each dictionary represents a contact. The new contact 
        will be added to this list.

    Returns
    -------
    None
        
    '''
    first_name = input("Enter First Name: ").strip().capitalize()
    last_name = input("Enter Last Name: ").strip().capitalize()
    
    phone = input('Enter Phone (format: (XXX)XXX-XXXX): ').strip()
    if validate_phone(phone):
        email = input('Enter Email: ').strip()
        if validate_email(email):
            contacts.append({'FirstName': first_name, 'LastName': last_name, 'Phone': phone, 'Email': email})
            print('Contact successfully added.')
        else:
            print('Invalid email format. Please try again.')
    else:
        print('Invalid phone format. Please try again.')
        

# validate phone format
def validate_phone(phone):
    
    return (
        len(phone) == 13 and 
        phone[0] == '(' and 
        phone[4] == ')' and 
        phone[8] == '-' and 
        phone[1:4].isdigit() and 
        phone[5:8].isdigit() and 
        phone[9:].isdigit()
    )

# validate email format
def validate_email(email):
    
    return '@' in email and '.' in email

# display contacts
def view_contacts(contacts):
    
    '''
    displays the list of contacts in a formatted table.

    Parameters
    ----------
    contacts : list of dict
        a list where each dictionary represents a contact, with keys 
        corresponding to 'FirstName', 'LastName', 'Phone', and 'Email'.

    Returns
    -------
    None
        
    '''
    
    print('\nContacts:')
    print()
    print(f'{"First Name":<15} {"Last Name":<15} {"Phone":<17} {"Email":<30}')
    print('-' * 75)
    for contact in contacts:
        print(f'{contact["FirstName"]:<15} {contact["LastName"]:<15} {contact["Phone"]:<17} {contact["Email"]:<30}')
        
        
# search for a contacts
def search_contact(contacts):
    
    '''
    searches for contacts by last name.

    Parameters
    ----------
    contacts : list of dict
        a list where each dictionary represents a contact. The function 
        searches through this list for contacts with the specified last name.

    Returns
    -------
    None
        
    '''
    
    last_name = input('Enter Last Name to search: ').strip().capitalize()
    found_contacts = [c for c in contacts if c['LastName'] == last_name]
    
    if found_contacts:
        view_contacts(found_contacts)
    else:
        print('Contact NOT found.')
        
        
# remove a contact
def remove_contact(contacts):
    
    '''
    removes a contact from the list based on the provided name.

    Parameters
    ----------
    contacts : list of dict
        a list where each dictionary represents a contact. The function 
        removes a contact from this list.

    Returns
    -------
    None
        
    '''
    first_name = input('Enter First Name of the contact to remove: ').strip().capitalize()
    last_name = input('Enter Last Name of the contact to remove: ').strip().capitalize()
    
    for contact in contacts:
        if contact['FirstName'] == first_name and contact['LastName'] == last_name:
            contacts.remove(contact)
            print('Contact successfully removed.')
            return
    print('Contact NOT found.')
    
    
# update a contact
def update_contact(contacts):
    
    '''
    updates the phone number of an existing contact.

    Parameters
    ----------
    contacts : list of dict
        a list where each dictionary represents a contact. The function 
        updates the phone number of a contact within this list.

    Returns
    -------
    None
        
    '''   
    print()
    last_name = input('Enter Last Name of the contact to update: ').strip().capitalize()
    found_contacts = [c for c in contacts if c['LastName'] == last_name]
    
    if found_contacts:
        view_contacts(found_contacts)
        first_name = input('Enter First Name to confirm the update: ').strip().capitalize()
        
        for contact in found_contacts:
            if contact['FirstName'] == first_name:
                new_phone = input('Enter new Phone (format: (XXX)XXX-XXXX): ').strip()
                while not validate_phone(new_phone):
                    print('Invalid phone format. Please try again.')
                    new_phone = input('Enter new Phone (format: (XXX)XXX-XXXX): ').strip()
                contact['Phone'] = new_phone
                print('Contact updated successfully.')
                return
        print('Contact NOT found.')
        
    else:
        print('Contact NOT found.')

        
# menu          
def menu():
    
    print('\n------Menu---------')
    print('1) Add Contact')
    print('2) View Contacts')
    print('3) Search Contact')
    print('4) Remove Contact')
    print('5) Update Contact')
    print('6) Exit')
    print('-' * 19)
    
    

if __name__ == "__main__":
    main()
    
    
    
    
    
