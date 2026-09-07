import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

categories = ['AI', 'Fintech', 'SaaS', 'E-commerce', 'Healthtech', 'Cybersecurity', 'Web3', 'Edtech']
acquirers = ['Google', 'Microsoft', 'Apple', 'Meta', 'Amazon', 'Salesforce', 'Adobe', 'Oracle']

def generate_historical_data(num_records=100):
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)

    for _ in range(num_records):
        date = fake.date_between(start_date=start_date, end_date=end_date)
        company = fake.company()
        category = random.choice(categories)
        acquirer = random.choice(acquirers)
        value = random.uniform(50_000_000, 5_000_000_000)

        data.append({
            'Date': date,
            'Company': company,
            'Category': category,
            'Acquirer': acquirer,
            'Value ($M)': value / 1_000_000,
            'Type': random.choice(['M&A', 'Sale', 'Exit'])
        })

    df = pd.DataFrame(data)
    return df

def generate_live_data(num_records=20):
    data = []
    for _ in range(num_records):
        company = fake.company()
        category = random.choice(categories)
        potential_acquirers = random.sample(acquirers, k=random.randint(1, 3))
        valuation = random.uniform(50_000_000, 2_000_000_000)

        data.append({
            'Company': company,
            'Category': category,
            'Potential Acquirers': ', '.join(potential_acquirers),
            'Estimated Valuation ($M)': valuation / 1_000_000,
            'Status': 'In Talks'
        })

    df = pd.DataFrame(data)
    return df

def mock_rag_categorization(company_description):
    """
    Mocks a RAG pipeline that categorizes a company based on a description.
    In a real app, this would query an LLM/Vector DB.
    """
    desc_lower = company_description.lower()
    if any(keyword in desc_lower for keyword in ['ai', 'machine learning', 'neural']):
        return 'AI'
    elif any(keyword in desc_lower for keyword in ['finance', 'bank', 'payment']):
        return 'Fintech'
    elif any(keyword in desc_lower for keyword in ['health', 'medical', 'doctor']):
        return 'Healthtech'
    elif any(keyword in desc_lower for keyword in ['security', 'protect', 'firewall']):
        return 'Cybersecurity'
    else:
        return 'SaaS'

def get_company_profile(company_name):
     """
     Generates a mock profile for a company, simulating a RAG retrieval.
     """
     description = fake.catch_phrase()
     products = [fake.bs() for _ in range(random.randint(1, 4))]
     inferred_category = mock_rag_categorization(description)

     return {
         'Company': company_name,
         'Description': description,
         'Products': products,
         'Inferred Category': inferred_category
     }

if __name__ == '__main__':
    print("Historical:")
    df_hist = generate_historical_data(2)
    print(df_hist)
    print("\nLive:")
    df_live = generate_live_data(2)
    print(df_live)
    print("\nProfile:")
    print(get_company_profile("Test Corp"))
