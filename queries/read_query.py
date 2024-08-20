def read_query(file_path):
    with open(file_path, 'r') as file:
        return file.read()
        
        
if __name__ == '__main__':
    print(read_query('google_ads_campaigns_costs.sql'))