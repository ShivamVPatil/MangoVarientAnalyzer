import streamlit as st
import pandas as pd
from PIL import Image
from keras.preprocessing.image import load_img,img_to_array
import numpy as np
from keras.models import load_model
import sqlite3 
conn = sqlite3.connect('data(3).sqlite')
c = conn.cursor()
import pydeck as pdk

from urllib.error import URLError

model = load_model('./Model/BC.h5',compile=False)
lab = {0: 'HealthyBadami', 1: 'HealthyTotapuri', 2: 'PartiallyRipeBadami', 3: 'PartiallyRipeTotapuri', 4: 'RawBadami', 5: 'RawTotapuri', 6: 'RottenBadami', 7: 'RottenNeelam', 8: 'RottenTotapuri', 9: 'UnripeBadami', 10: 'UnripeTotapuri'}

global result


def sql_executor(raw_code):
	c.execute(raw_code)
	data = c.fetchall()
	return data 


def processed_img(img_path):
    img=load_img(img_path,target_size=(224,224,3))
    img=img_to_array(img)
    img=img/255
    img=np.expand_dims(img,[0])
    answer=model.predict(img)
    y_class = answer.argmax(axis=-1)
    print(y_class)
    y = " ".join(str(x) for x in y_class)
    y = int(y)
    res = lab[y]
    print(res)
    return res

#main
st.title("")
st.markdown("##")


state = {}
links = ["https://earthjustice.org/features/what-you-need-to-know-about-chlorpyrifos","https://www.nationalgeographic.com/environment/article/chlorpyrifos-insecticides-pesticides-epa-organophosphates","https://repository.usfca.edu/cgi/viewcontent.cgi?article=1553&context=capstone","https://www.downtoearth.org.in/coverage/health/tracking-decades-long-endosulfan-tragedy-in-kerala-56788","https://wwwn.cdc.gov/TSP/PHS/PHS.aspx?phsid=607&toxid=113","https://pubmed.ncbi.nlm.nih.gov/29705383/"]



menu = ["Home","About","Read more"]
options_cult= ["totapuri","badami"]
choice = st.sidebar.selectbox("Menu",menu)
def str_home():
  if choice == "Home":
    st.title("Fruit Selector")
    img_file = st.file_uploader("Select image for input:", type=["jpg", "png","jpeg"])
    if img_file is not None:
        st.image(img_file,use_column_width=False)
        save_image_path = './upload_images/'+img_file.name
        with open(save_image_path, "wb") as f:
            f.write(img_file.getbuffer())


    
    if st.button("Select"):
        result = processed_img(save_image_path)
        st.success("Predicted Varient is: "+result)
        return(result)
        


str_home()


if choice == "About":
  
      st.write("Enter your predicted varient:")
      cultivar =st.selectbox("Cultivar: ",options=options_cult)
      y = cultivar
      if y =="totapuri":
        cultivar = ("totapuri")
        season = ("May -> June")
        state = {'state':['Tamil nadu','Gujrat'],'lat':[11.1271,22.2587],'lon':[78.6569,71.1924]}
        uses = ("Sweet and tangy in taste, Totapuri mango is great for processing pulp. Best to use it for making juice, concentrate, shakes, etc")
      elif y == 'HealthyBadami' or 'PartiallyRipeBadami' or 'RawBadami' or 'RottenBadami' or 'UnripeBadami' or 'badami':
        cultivar = ("badami")
        season = ("July -> March")
        state = {'state':['Maharashtra','Gujrat','Karnataka'],'lat':[19.7515,22.2587,15.3173],'lon':[75.7139,71.1924,75.7139]}
        uses = ("Generally eaten raw, Badami mango is known for it's size and wonderful aroma. This is also the costliest cultivar of mango in India")
    

      
      query11 = "SELECT DISTINCT pesticides_used,toxic FROM pesticide WHERE pesticides_used IN (SELECT pesticides_used FROM statewise_pesticide WHERE state IN (SELECT state FROM statewise_mango WHERE mango_cultivar = '"+str(cultivar)+"'));"
      query12 = "SELECT DISTINCT state FROM statewise_mango WHERE mango_cultivar = '"+str(cultivar)+"';"
      query11_result = sql_executor(query11)
      query12_result = sql_executor(query12)
      query11_df = pd.DataFrame(query11_result,columns=['Pesticide','Toxic'])
      rslt_df = query11_df[(query11_df['Toxic'] =='high')]
      query12_df = pd.DataFrame(query12_result)




      st.markdown("##")
      st.header("States where " +str(y)+ " mango is grown:")
      state_df = pd.DataFrame(state)
      st.map(state_df,zoom = 3)
      st.header("Seasonality:")
      st.write(season)
      st.header("Common uses:")
      st.write(uses)
      st.subheader("Most toxic pesticides found in these states for this cultivar:")
      st.dataframe(rslt_df)
      
      
      
      

  
   
      query2 = "SELECT mango_cultivar,off_season_start,off_season_end FROM cultivarwise_season WHERE mango_cultivar= '"+str(cultivar)+"';"
      query2_result = sql_executor(query2)

      
      st.subheader("BEWARE")
      query3 = "SELECT state,avg_half_life FROM half_life WHERE state IN (SELECT state FROM statewise_mango WHERE mango_cultivar='"+str(cultivar)+"');"
      query3_result = sql_executor(query3)
      query3_df = pd.DataFrame(query3_result,columns=['State','Avg half life'])
      
      
      if y == 'badami':
        state1 = query3_df['State'][0]
        avg1 = query3_df['Avg half life'][0]
        state2 = query3_df['State'][1]
        avg2 = query3_df['Avg half life'][1]
        max = int(avg1) if int(avg1) > int(avg2) else int(avg2)
        percent = max - 23.5
        if max > 23.5:
         st.write("Average half life of pesticides used in ",state1,"is  more than average." )
      
      
      if y == 'totapuri':
        state1 = query3_df['State'][0]
        avg1 = query3_df['Avg half life'][0]
        state2 = query3_df['State'][1]
        avg2 = query3_df['Avg half life'][1]
        max = float(avg1) if float(avg1) > float(avg2) else float(avg2)
        percent = max - 23.5
        if max > 23.5:
         st.write("Average half life of pesticides used in ",state1,"is  more than average." )

        
     
      
      





if choice == "Read more":
  st.title("Related articles about most toxic pesticides.")
  col1, col2 = st.columns(2)
  
  with col1:
    st.header("Chlorpyrifos EC:")
    st.write("1) ",links[0])
    st.write("2) ",links[1])
    st.write("3) ",links[2])

  with col2:
    st.header("Endosulfan:")
    st.write("1) ",links[3])
    st.write("2) ",links[4])










          


    

      
        
