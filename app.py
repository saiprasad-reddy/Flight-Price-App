import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import streamlit as st

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=["GET","POST"])
@cross_origin()

def predict():
    '''
    For rendering results on HTML GUI
    '''
    if request.method == "POST":
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        Date_of_Journey = st.date_input("Date of Your Journey",tomorrow, min_value=today)
        Days_to_Departure=(Date_of_Journey - today).days
        Date_of_Journey = pd.to_datetime(Date_of_Journey, format="%Y/%m/%d")
        Weekend = int(np.where((Date_of_Journey.dayofweek) < 5,0,1))
        Source = st.selectbox('Source', ("Bengaluru", "New Delhi", "Mumbai", "Hyderabad", "Jaipur"))
        Destination = st.selectbox('Destination', ("New Delhi", "Bengaluru", "Mumbai", "Hyderabad","Jaipur"))
    
        if Source == Destination:
            st.error('Error: Source and Destination must be different.')

        Dep_Time = st.time_input("Departure Time", datetime.time(8, 45))
        Arr_Time = st.time_input("Arrival Time", datetime.time(11, 40))
        t1 = datetime.datetime.strptime(str(Dep_Time), '%H:%M:%S')
        t2 = datetime.datetime.strptime(str(Arr_Time), '%H:%M:%S')
        Duration=int((t2 - t1).seconds/60)
        d=float(Dep_Time.hour)
        a=float(Arr_Time.hour)
        def get_cat(dep):
            dep = int(dep)
            if (dep >= 0 and dep < 6):
                return 'Before 6AM'
            elif (dep >= 6 and dep < 12): 
                return '6AM-12PM'
            elif (dep >= 12 and dep < 18): 
                return '12PM-6PM'
            else: 
                return 'After 6PM'
        dep_session=get_cat(d)
        arr_session=get_cat(a)
        Airline = st.selectbox('Airline', ("IndiGo", "Vistara", "Spicejet", "AirAsia", "Go Air", "Air India","TruJet","Star Air"))
    
        total_stops = st.radio('Total Stops', (0, 1, 2, 3))  
        dt = pd.DataFrame([[Airline,Source, Destination, dep_session,arr_session ]], columns=['Airline', 'Source', 'Destination','dep_session' ,'arr_session'])
        l1 = pd.get_dummies(dt)
        enc = l1.reindex(columns = encodes.columns, fill_value=0)
        dff = pd.DataFrame([[np.log1p(Duration), total_stops, Days_to_Departure, Weekend]],columns=['total_stops', 'duration_mins',  'Days_to_Departure', 'Weekend'])
        final_df = pd.concat([dff,enc], axis=1)
        if st.button("Predict"):
            output=np.expm1(model.predict(final_df))
            output=round(output[0])
            st.success('The Price is {}'.format(output))
            st.success('Bon Voyage!')
            st.balloons()

if __name__ == "__main__":
    app.run(debug=True)
