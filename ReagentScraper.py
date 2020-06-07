import requests
import matplotlib.pyplot as plt
import numpy as np

def get_data():
    ''' returns dataset in json converted to python format '''
    base = 'http://comtrade.un.org/api/get?' # base api, documentation : https://comtrade.un.org/data/doc/api/#DataRequests
    payload = {'type' : 'C', 'freq' : 'A', 'px': 'HS', 'ps' : '2019', 'r': 'all', 'p' : '0', 'cc' : '382200', 'rg': 'all' } # params, note ps = year. cc = comoditity code

    r = requests.get(base, params=payload)
    jason = r.json()
    dataset = jason['dataset'] # dataset of api

    return dataset # list of dictionaries

def extract_data(dataset):
    ''' Takes json from get_data() and returns list of dictionaries for entries in form [{Country: , Flow: , Value:, Quantity:}, {}]'''

    trade = [] # holds a list of dictionaries where each dic is an entry in dataset holding {Country: , Flow: , Value:, Quantity:  }

    for entry in dataset:

        entry_dic = {}
        country = entry['rtTitle'] # country name
        trade_flow = entry['rgDesc'] # import, export, re-import, re-export
        trade_value = entry['TradeValue'] # value in usd
        trade_qnt = entry['TradeQuantity'] # units =  (kg)

        # creates dictionary
        entry_dic['Country'] = country
        entry_dic['Flow'] = trade_flow
        entry_dic['Value'] = trade_value
        entry_dic['Quantity'] = trade_qnt

        trade.append(entry_dic)

    return trade

def balance_data(extracted_data):
    ''' Takes a list of dics of unbalanced extracted data from extract_data(), returns list of dics of balanced country export/import data for value and qnt '''

    extracted_data = extracted_data # make local version as dont want to update global version

    balanced_list = [] # holds dictionaries of balanced countries

    for entry in extracted_data:

        country = entry['Country']

        if country != 'Checked': # make sure entry has not already been evaluated

            balanced_dic = {} # makes dictionary {Country: , Net_Import_Value: , Net_Export_Value: , Net_Import_Quantity: , Net_Export_Quantity: , }

            net_import_value = 0
            net_export_value = 0

            net_import_qnt = 0
            net_export_qnt = 0

            for entry in extracted_data: # Balances Countries import/export data for re-imports/re-exports

                if entry['Country'] == country: # checks to see if entry is same country

                    if entry['Flow'] == 'Import':
                        net_import_value += entry['Value']
                        net_import_qnt += entry['Quantity']
                    if entry['Flow'] == 'Re-Export':
                        net_import_value -= entry['Value']
                        net_import_qnt -= entry['Quantity']

                    if entry['Flow'] == 'Export':
                        net_export_value += entry['Value']
                        net_export_qnt += entry['Quantity']
                    if entry['Flow'] == 'Re-Import':
                        net_export_value -= entry['Value']
                        net_export_qnt -= entry['Quantity']

                    entry['Country'] = 'Checked' # Need to change country name so doesn't loop doesnt repeat for every entry

            balanced_dic['Country'] = country
            balanced_dic['Net_Import_Value'] = net_import_value
            balanced_dic['Net_Export_Value'] = net_export_value
            balanced_dic['Net_Import_Quantity'] = net_import_qnt
            balanced_dic['Net_Export_Quantity'] = net_export_qnt

            balanced_list.append(balanced_dic)

    return balanced_list

def graph_format(balanced_data):
    ''' Takes list of dics from balance_data and returns lists for categories when index is constant per country. countries, value_import, value_export, qnt_import, qnt_export '''
    countries = []
    value_import = []
    value_export = []
    qnt_import = []
    qnt_export = []

    for entry in balanced_data:
        countries.append(entry['Country'])
        value_import.append(entry['Net_Import_Value'])
        value_export.append(entry['Net_Export_Value'])
        qnt_import.append(entry['Net_Import_Quantity'])
        qnt_export.append(entry['Net_Export_Quantity'])

    return countries, value_import, value_export, qnt_import, qnt_export

def value_graph(countries, value_import, value_export):
    ''' Creates a 2-part bar graph for values of import/export by country '''
    divisions = countries
    imports = value_import
    exports = value_export

    index = np.arange(len(divisions))
    width = 0.20

    plt.bar(index, imports, width, color='green', label='Net Import Value (USD)')
    plt.bar(index+width, exports, width, color='blue', label='Net Export Value (USD)')
    plt.title('Import/Export of Reagents by Country in USD - 2019')

    plt.ylabel('Billion USD')
    plt.xlabel('Country')
    plt.xticks(index + width/2, countries, rotation='vertical') # ticks to divide import / export
    plt.legend(loc='best')

    plt.show()

def quantity_graph(countries, qnt_import, qnt_export):
    ''' Creates a 2-part bar graph for values of import/export by country '''
    divisions = countries
    imports = qnt_import
    exports = qnt_export

    index = np.arange(len(divisions))
    width = 0.20

    plt.bar(index, imports, width, color='green', label='Net Import Quantity')
    plt.bar(index+width, exports, width, color='blue', label='Net Export Quantity')
    plt.title('Import/Export of Reagent Quantities (kg) by Country  - 2019')

    plt.ylabel('Quantity (kg)')
    plt.xlabel('Country')
    plt.xticks(index + width/2, countries, rotation='vertical') # ticks to divide import / export
    plt.legend(loc='best')

    plt.show()


def main():

    # Data Wrangling
    dataset = get_data()
    extracted_data = extract_data(dataset)
    balanced_data = balance_data(extracted_data)
    graphing_data = graph_format(balanced_data)

    # Retrieving graphing data
    Countries = graphing_data[0]
    value_import = graphing_data[1]
    value_export = graphing_data[2]
    qnt_import = graphing_data[3]
    qnt_export = graphing_data[4]

    # Graphs
    value_graph(Countries, value_import, value_export)
    quantity_graph(Countries, qnt_import, qnt_export)

if __name__ == '__main__':
    main()
