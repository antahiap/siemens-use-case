import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

st.set_option('deprecation.showPyplotGlobalUse', False)

class pred_consumtion:
    def __init__(self, year_now, month_now, length, SM):
        # Linear Regression for yearly
        nYear = int(length/12)
     
        months, years = [], []
        m0 = month_now
        yi = year_now
        while len(months) < length:
            while m0 < 13 and len(months) < length:
                months.append(m0)
                years.append(yi)
                m0+=1
            m0 = 1
            yi +=1
        self.X_df = pd.DataFrame()
        self.X_df['Year']= years
        self.X_df['Month'] = months

        self.SM = SM
    

    def monthly(self, model, RMSE):

        safety_margin = self.SM / 100 * RMSE
    
        self.pred = int(model.predict(self.X_df).sum() )
        self.pred2 = int(self.pred + safety_margin)
        return self.print_pred(RMSE)

    def yearly(self, model, RMSE):
        
        X2 =pd.DataFrame()
        X2['Year'] = self.X_df.loc[:, 'Year'].unique()
        # count number of month per year
        count = []
        for xi in X2.Year:
            yr_msk = self.X_df['Year'] == xi
            count.append(self.X_df.loc[yr_msk].Year.count())
        
        X = X2.loc[:, 'Year'].values.reshape(-1, 1)
        pred = model.predict(X)* np.array(count)/12

        safety_margin = self.SM / 100 * RMSE

        self.pred = int(pred.sum())
        self.pred2 = int(self.pred + safety_margin)
        return self.print_pred(RMSE)

    def print_pred(self, RMSE):
        txt = (
            f'  - RMSE on the test data: {int(RMSE)}\n' +
            f'  - The future cost prediction: {self.pred}\n' +
            f'  - with {self.SM}% safety margin = {self.pred2}\n')
        return txt

def load_pickles(model_pickle_path):
    model_pickle_opener = open(model_pickle_path, "rb")
    model = pickle.load(model_pickle_opener)

    return model

def generate_prediction(year, month, length, model, SM):

    m_name = '_'.join(model.lower().split(' '))
    m_path = f'model/{m_name}.pkl'

    model = load_pickles(m_path)
    P = pred_consumtion(year, month,length, SM)
    
    rmse = pd.read_csv("./model/rmse.csv", sep=',')
    rmse_m = rmse[m_name]

    if m_name == 'linear_regression':
        txt = P.yearly(model, rmse_m)
    else:
        txt = P.monthly(model, rmse_m)
   
    return txt

def plot_test_3(models):

    for model in models:
        m_name = '_'.join(model.lower().split(' '))
        data_y = pd.read_csv(f"./data/{m_name}_test.csv", sep=',')
        sns.regplot(x='y', y='y_pred', data=data_y, label=f'{m_name}')


    # Set plot labels and title
    plt.xlabel('True Values')
    plt.ylabel('Predicted Values')
    plt.title('Comparison of 3 models')

    # Add legend
    plt.legend()
    st.pyplot()


if __name__ == '__main__':
    # make the application
    st.title("Consumtion Prediction")


    # importing customer churn data
    data = pd.read_csv("./data/consumption.csv", sep=';')

    # List of options for the dropdown menu
    models = ['Linear Regression', 'Random Forest', 'Decision Tree']

    col1, col2 = st.columns(2)
    with col1:
        st.write("Material Data")
        st.write(data)
    with col2:
        st.write("Prediction overview")
        plot_test_3(models)


    
    
    # model list
    
    # Create multiple columns
    col1, col2 = st.columns(2)
    # Add content to each column
    model = col1.selectbox('Select a model:', models)
    SM = col2.slider('Prediction Safety Margin:', min_value=0, max_value=100, value=20)
    
    # Prediction time selection
    # List of year options for the dropdown menu
    year_options = list(range(2023, 2030))  
    month_options = list(range(1, 12))
    
    # Create select boxes in three columns
    col1, col2, col3 = st.columns(3)
    
    year = col1.selectbox('Year:', year_options)
    month = col2.selectbox('Month:', month_options)
    length = col3.slider('Forcasting Interval (No. months):', min_value=1, max_value=100, value=24)
    
    # generate the prediction
    if st.button("Predict Consumtion"):
        pred = generate_prediction(year, month, length, model, SM)
        st.text(pred)

        # plot the prediction over train, test data
        st.write(f"{model} training vs test data")

        m_name = '_'.join(model.lower().split(' '))
        data_y = pd.read_csv(f"./data/{m_name}_train.csv", sep=',')
        sns.regplot(x='y', y='y_pred', data=data_y, label='Train')


        data_y = pd.read_csv(f"./data/{m_name}_test.csv", sep=',')
        sns.regplot(x='y', y='y_pred', label='Test', data=data_y)


        # Set plot labels and title
        plt.xlabel('True Values')
        plt.ylabel('Predicted Values')
        plt.title(f"{model} training vs test data")
        plt.legend()
    
        st.pyplot()
