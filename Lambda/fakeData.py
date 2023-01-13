
# Importing the required libraries for the program to run.
import csv
import os
import random

from faker import Faker
from faker.providers import (
    bank,
    DynamicProvider,
)

# This is creating a fake data generator.
fake = Faker('en_US')

fake_loan_type_provider = DynamicProvider(
provider_name = "loan_type",
elements=["property", "automobile", "personal", "line of credit", "recreational", "business"],
)

fake.add_provider(fake_loan_type_provider)
fake.add_provider(bank)

# Creating a path to save the file in the /tmp directory.
save_path = ("/tmp/")
file_name = "account_data.csv"

path_filename = os.path.join(save_path, file_name)

def datagenerate(records, headers):
    """
    It creates a csv file with the given headers and generates random data for each of the headers.
    
    :param records: The number of records you want to generate
    :param headers: This is a list of the column names that will be in the CSV file
    """

    with open(path_filename, 'wt') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
        writer.writeheader()
        for i in range(records):
            Fname = fake.first_name()
            Lname = fake.last_name()
            Name = Fname + ' ' + Lname
            domain_name = "@example.com"
            emailAddress = Fname +"."+ Lname + domain_name
            
            writer.writerow({
                    "Name": Name,
                    "PhoneNumber" : fake.phone_number(),
                    "Address" : f"{fake.street_address()},{fake.city()},{fake.state()}-{fake.postcode()}",
                    "EmailAddress" : emailAddress,
                    "AccountNum" : fake.bban(),
                    "LoanType" : fake.loan_type(),
                    "LoanAmount" : round(random.randint(100000, 100000000)/1000)*1000,
                    "IncomeAmount" : round(random.randint(80000, 600000)/1000)*1000,
                    "LoanApproval" : fake.boolean(chance_of_getting_true= 65),
                    "CheckingBalance" : fake.pricetag(),
                    "SavingsBalance" : fake.pricetag(),
                    "AccountOpenDate" : fake.date(),
                    })
    
