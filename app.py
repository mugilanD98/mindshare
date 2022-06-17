from secrets import choice
import streamlit as st
import pandas as pd
import openpyxl
import numpy as np
import statistics
import time
from statistics import stdev
import base64
import io
from io import StringIO, BytesIO
import math
import plotly.graph_objects as go


st.title("Automation Dashboard")
def main():
    menu=['Seat Classification','Sensitivity Graph']
    choice=st.sidebar.selectbox("Menu",menu)

    if choice == "Seat Classification":
        st.subheader("Seat Classification")
        data_file=st.file_uploader("upload file")
        st.write(data_file)
        df=pd.read_excel(data_file,sheet_name = None)
        sheet=df.keys()
        agree = st.multiselect('Sheet Names',sheet)
        print(agree)
        df1=pd.read_excel(data_file,sheet_name = agree[0])
        #st.dataframe(df1)
        col=df1.columns
        st.sidebar.subheader("Select Column Below")
        Constituency_No_Input=st.sidebar.selectbox("Constituency_No",col)
        Year_Input=st.sidebar.selectbox("Year",col)
        Election_Type_Input=st.sidebar.selectbox("Election Type",col)
        Party_Input=st.sidebar.selectbox("Party",col) 
        Votes_Input=st.sidebar.selectbox("Votes",col)
        Valid_Votes_Input=st.sidebar.selectbox("Valid Votes",col)
        Rank_Input=st.sidebar.selectbox("Rank",col)

        st.subheader("Give Values")
        Party_Name_input=st.text_input("Party Name")
        Election_Type_value_input=st.text_input("Election Type")
        recent_year1_input=st.text_input("Initial Year")
        recent_year2_input=st.text_input("Mid Year")
        recent_year3_input=st.text_input("Recent Year")

        st.subheader("Give Weights")
        tolerance_weight_input=st.text_input("Tolerance %")
        recent_year_weight_input=st.text_input("Weight for Recent Year")
        mid_year_weight_input=st.text_input("Weight for Middle Year")
        initial_year_weight_input=st.text_input("Weight for Initial Year")
        AE_score_weight_input=st.text_input("Weight for AE Score")
        AC_Score_weight_input=st.text_input("Weight for AC Score")
        winloss_weight_input=st.text_input("Weight for Final WinLoss Score")
        margin_weight_input=st.text_input("Weight for Final Margin Score")
        voteshare_weight_input=st.text_input("Weight for Final Vote Share Score")

        st.subheader("Give Category Range")
        safe_range_input=st.text_input("Range for Safe")
        favorable_range_input=st.text_input("Range for Favorable")
        difficult_range_input=st.text_input("Range for Difficult")
        bg_range_input=st.text_input("Range for Battle Ground")
        #time.sleep(100)
        #input("You can't see the next text. (press enter)")
        # input() waits for a user input
        #print("Now you can!")        
        if st.checkbox('Run'):


            user_input={"file_name":data_file,"sheet_names":agree,"attributes_names": {"state":"State_Name" ,"year":Year_Input,"election_type":Election_Type_Input,"party":Party_Input,"constituency_no":Constituency_No_Input,"constituency_name":"Constituency_Name","Rank":Rank_Input,"votes":Votes_Input,"valid_votes":Valid_Votes_Input,"Vote share %":"VS%" ,"margin":"Margin"},"values": {"election_type":Election_Type_value_input.upper(),"initial_year1":int(recent_year1_input),"initial_year2":int(recent_year2_input),"initial_year3":int(recent_year3_input),"party":Party_Name_input.upper()},"weights": {"tolerance %":float(tolerance_weight_input),"winloss_AE_weight": {"recent_year":float(recent_year_weight_input),"mid_year":float(mid_year_weight_input),"initial_year":float(initial_year_weight_input)},"margin_AE_weight": {"recent_year":float(recent_year_weight_input),"mid_year":float(mid_year_weight_input),"initial_year":float(initial_year_weight_input)},"vote_share_AE_weight": {"recent_year":float(recent_year_weight_input),"mid_year":float(mid_year_weight_input),"initial_year":float(initial_year_weight_input)},"margin_change_final_score_weight": {"for_AE_score":float(AE_score_weight_input),"for_AC_score":float(AC_Score_weight_input)},"voteshare_change_final_score_weight": {"for_AE_score":float(AE_score_weight_input),"for_AC_score":float(AC_Score_weight_input)},"net_score_weight": {"for_winloss_AE_score":float(winloss_weight_input),"for_margin_final_score":float(margin_weight_input),"for_voteshare_final_score":(float(voteshare_weight_input)/100)*60,"for_voteshare_AC_score":(float(voteshare_weight_input)/100)*40}},"category_range": {"safe":float(safe_range_input),"Favorable":float(favorable_range_input),"Difficult":float(difficult_range_input),"Battleground":float(bg_range_input)}}
            
            processed_data=pd.DataFrame(columns=['Constituency_No', 'Year', 'Election_Type', 'Constituency_Name','Party', 'Position', 'Votes', 'Valid_Votes', 'vote_share%', 'margin'])
            ae_sheets = user_input['sheet_names']
            for l in ae_sheets:
                raw_data = pd.read_excel(user_input['file_name'],sheet_name=l)
                raw_data=raw_data[[user_input['attributes_names']['constituency_no'],user_input['attributes_names']['election_type'],user_input['attributes_names']['year'],user_input['attributes_names']['constituency_name'],user_input['attributes_names']['party'],user_input['attributes_names']['Rank'],user_input['attributes_names']['votes'],user_input['attributes_names']['valid_votes']]]
                raw_data=raw_data.rename(columns={user_input['attributes_names']['constituency_no']:'Constituency_No',user_input['attributes_names']['year']:'Year',user_input['attributes_names']['election_type']:'Election_Type',user_input['attributes_names']['constituency_name']:'Constituency_Name',user_input['attributes_names']['party']:'Party',user_input['attributes_names']['Rank']:'Position',user_input['attributes_names']['votes']:'Votes',user_input['attributes_names']['valid_votes']:'Valid_Votes'})
                raw_data['vote_share%']=(raw_data['Votes']/raw_data['Valid_Votes'])*100
                raw_data['vote_share%']=round(raw_data['vote_share%'],2)
                
                margin_list=[]
                for i in range(len(raw_data['Constituency_No'])):
                    if raw_data.loc[i,'Party']==user_input['values']['party'] and raw_data.loc[i,'Position']==1:
                        for j in range(len(raw_data['Constituency_No'])):
                            if raw_data.loc[j,'Constituency_No']==raw_data.loc[i,'Constituency_No'] and raw_data.loc[j,'Position']==2:
                               c_margin=raw_data.loc[i,'vote_share%']-raw_data.loc[j,'vote_share%']
                               margin_list.append([raw_data.loc[i,'Constituency_No'],c_margin])
                            else:
                                a=0
                    elif raw_data.loc[i,'Party']==user_input['values']['party'] and raw_data.loc[i,'Position']!=1: 
                        for k in range(len(raw_data['Constituency_No'])):
                            if raw_data.loc[k,'Constituency_No']==raw_data.loc[i,'Constituency_No'] and raw_data.loc[k,'Position']==1:
                               cal_margin=raw_data.loc[i,'vote_share%']-raw_data.loc[k,'vote_share%']
                               margin_list.append([raw_data.loc[i,'Constituency_No'],cal_margin])
                            else:
                               a=0
                    else:
                        a=0      
                margin_data=pd.DataFrame(margin_list,columns=['constituency_no','margin'])
                pre_voteshare_margin=raw_data.merge(margin_data,left_on='Constituency_No', right_on='constituency_no', how='left')
                pre_voteshare_margin=pre_voteshare_margin[['Constituency_No','Year','Election_Type','Constituency_Name','Party','Position','Votes','Valid_Votes','vote_share%','margin']]
                pre_voteshare_margin=pre_voteshare_margin[pre_voteshare_margin['Party']==user_input['values']['party']]
                processed_data=processed_data.append(pre_voteshare_margin)

            

    
            # calculation
            data=processed_data.copy()
            data=data.rename(columns={'Position':'Rank','vote_share%':'VS%','margin':'Margin'})

            datamap=data['Constituency_No'].unique().tolist()
            datamap_df=pd.DataFrame(datamap,columns=['map_Constituency_No'])

            data=data[data['Party']==user_input['values']['party']]
            data=data[data['Election_Type']==user_input['values']['election_type']]

            data_2018=data[data['Year']==user_input['values']['initial_year3']]     
            data_2014=data[data['Year']==user_input['values']['initial_year2']]
            data_2009=data[data['Year']==user_input['values']['initial_year1']]

            win_loss_2018=datamap_df.merge(data_2018,left_on='map_Constituency_No', right_on='Constituency_No', how='left')
            win_loss_2014=datamap_df.merge(data_2014,left_on='map_Constituency_No', right_on='Constituency_No', how='left')
            win_loss_2009=datamap_df.merge(data_2009,left_on='map_Constituency_No', right_on='Constituency_No', how='left')
            win_loss_df=win_loss_2018[['map_Constituency_No','Rank']]
            win_loss_df['Rank_2014']=win_loss_2014['Rank']
            win_loss_df['Rank_2009']=win_loss_2009['Rank']
            win_loss_df=win_loss_df.rename(columns={'Rank':'Rank_2018'})    



            ae_score_winloss=[]
            for i in range(len(win_loss_df['map_Constituency_No'])):
                if win_loss_df['Rank_2018'][i]==1 and win_loss_df['Rank_2014'][i]==1 and win_loss_df['Rank_2009'][i]==1:
                    ae_score_winloss.append(user_input['weights']['winloss_AE_weight']['recent_year']+user_input['weights']['winloss_AE_weight']['mid_year']+user_input['weights']['winloss_AE_weight']['initial_year'])
                elif win_loss_df['Rank_2018'][i]==1 and win_loss_df['Rank_2014'][i]==1:
                    ae_score_winloss.append(user_input['weights']['winloss_AE_weight']['recent_year']+user_input['weights']['winloss_AE_weight']['mid_year'])
                elif win_loss_df['Rank_2014'][i]==1 and win_loss_df['Rank_2009'][i]==1:
                    ae_score_winloss.append(user_input['weights']['winloss_AE_weight']['mid_year']+user_input['weights']['winloss_AE_weight']['initial_year'])
                elif win_loss_df['Rank_2009'][i]==1 and win_loss_df['Rank_2018'][i]==1:
                    ae_score_winloss.append(user_input['weights']['winloss_AE_weight']['initial_year']+user_input['weights']['winloss_AE_weight']['recent_year'])
                elif win_loss_df['Rank_2018'][i]==1:
                    ae_score_winloss.append(user_input['weights']['winloss_AE_weight']['recent_year'])     
                elif win_loss_df['Rank_2014'][i]==1:
                    ae_score_winloss.append(user_input['weights']['winloss_AE_weight']['mid_year'])
                elif win_loss_df['Rank_2009'][i]==1:
                    ae_score_winloss.append(user_input['weights']['winloss_AE_weight']['initial_year'])
                else:
                    ae_score_winloss.append(0)  
            win_loss_df['ae_score_winloss']=ae_score_winloss
            margin_2018=datamap_df.merge(data_2018,left_on='map_Constituency_No', right_on='Constituency_No', how='left')    # margin
            margin_2018=margin_2018['Margin']
            win_loss_df['margin']=margin_2018
            win_loss_df['margin-mean(m)']=win_loss_df['margin']-win_loss_df['margin'].mean()
            win_loss_df['std(m)']=win_loss_df['margin'].std()
            win_loss_df['sigma(m)']=win_loss_df['margin-mean(m)']/win_loss_df['std(m)']

            margins_2018=[]        
            for i in range(len(win_loss_df['map_Constituency_No'])):
                if win_loss_df['sigma(m)'][i]<-2:
                    margins_2018.append(0)
                elif win_loss_df['sigma(m)'][i]<-1:
                    margins_2018.append(0.2)  
                elif win_loss_df['sigma(m)'][i]<-0.5:
                    margins_2018.append(0.3)
                elif win_loss_df['sigma(m)'][i]<0:
                    margins_2018.append(0.4)  
                elif win_loss_df['sigma(m)'][i]>2:
                    margins_2018.append(1)
                elif win_loss_df['sigma(m)'][i]>=1:
                    margins_2018.append(0.8)
                elif win_loss_df['sigma(m)'][i]>0.5:
                    margins_2018.append(0.6)
                elif win_loss_df['sigma(m)'][i]>0:
                    margins_2018.append(0.5) 
                else:
                    margins_2018.append(np.nan)   # doubt
            win_loss_df['score_margin_2018']=margins_2018     

            margin_2014=datamap_df.merge(data_2014,left_on='map_Constituency_No', right_on='Constituency_No', how='left')
            margin_2014=margin_2014['Margin']
            win_loss_df['margin_2014']=margin_2014
            win_loss_df['margin-mean(m)2014']=win_loss_df['margin_2014']-win_loss_df['margin_2014'].mean()
            win_loss_df['std(m)2014']=win_loss_df['margin_2014'].std()
            win_loss_df['sigma(m)2014']=win_loss_df['margin-mean(m)2014']/win_loss_df['std(m)2014']
            margins_2014=[]
            for i in range(len(win_loss_df['map_Constituency_No'])):
                if win_loss_df['sigma(m)2014'][i]<-2:
                    margins_2014.append(0)
                elif win_loss_df['sigma(m)2014'][i]<-1:
                    margins_2014.append(0.2)  
                elif win_loss_df['sigma(m)2014'][i]<-0.5:
                    margins_2014.append(0.3)
                elif win_loss_df['sigma(m)2014'][i]<0:
                    margins_2014.append(0.4)  
                elif win_loss_df['sigma(m)2014'][i]>2:
                    margins_2014.append(1)
                elif win_loss_df['sigma(m)2014'][i]>1:
                    margins_2014.append(0.8)
                elif win_loss_df['sigma(m)2014'][i]>0.5:
                    margins_2014.append(0.6)
                elif win_loss_df['sigma(m)2014'][i]>0:
                    margins_2014.append(0.5) 
                else:
                    margins_2014.append(np.nan)   # doubt
            win_loss_df['score_margin_2014']=margins_2014
            margin_2009=datamap_df.merge(data_2009,left_on='map_Constituency_No', right_on='Constituency_No', how='left')
            margin_2009=margin_2009['Margin']
            win_loss_df['margin_2009']=margin_2009
            win_loss_df['margin-mean(m)2009']=win_loss_df['margin_2009']-win_loss_df['margin_2009'].mean()
            win_loss_df['std(m)2009']=win_loss_df['margin_2009'].std()
            win_loss_df['sigma(m)2009']=win_loss_df['margin-mean(m)2009']/win_loss_df['std(m)2009']  
            margins_2009=[]
            for i in range(len(win_loss_df['map_Constituency_No'])):
                if win_loss_df['sigma(m)2009'][i]<-2:
                    margins_2009.append(0)
                elif win_loss_df['sigma(m)2009'][i]<-1:
                    margins_2009.append(0.2)  
                elif win_loss_df['sigma(m)2009'][i]<-0.5:
                    margins_2009.append(0.3)
                elif win_loss_df['sigma(m)2009'][i]<0:
                    margins_2009.append(0.4)  
                elif win_loss_df['sigma(m)2009'][i]>2:
                    margins_2009.append(1)
                elif win_loss_df['sigma(m)2009'][i]>1:
                    margins_2009.append(0.8)
                elif win_loss_df['sigma(m)2009'][i]>0.5:
                    margins_2009.append(0.6)
                elif win_loss_df['sigma(m)2009'][i]>0:
                    margins_2009.append(0.5) 
                else:
                    margins_2009.append(np.nan)   # doubt
            win_loss_df['score_margin_2009']=margins_2009                      
            win_loss_df['ac_tolerance_margin_2009_by_5%']=user_input['weights']['tolerance %']*abs(win_loss_df['margin_2009'])
            margins_ac_score=[]
            for i in range(len(win_loss_df['map_Constituency_No'])):
                if win_loss_df['margin'][i]>(win_loss_df['ac_tolerance_margin_2009_by_5%'][i])+(win_loss_df['margin_2009'][i]):
                    margins_ac_score.append(1)
                elif win_loss_df['margin'][i]<=-win_loss_df['ac_tolerance_margin_2009_by_5%'][i]+win_loss_df['margin_2009'][i]:
                    margins_ac_score.append(0) 
                else:
                    margins_ac_score.append(0.5)

            win_loss_df['margins_ac_score']=margins_ac_score            
            margins_ae_score=[]
            win_loss_df['score_margin_2018']=win_loss_df['score_margin_2018'].fillna(0)
            win_loss_df['score_margin_2014']=win_loss_df['score_margin_2014'].fillna(0)
            win_loss_df['score_margin_2009']=win_loss_df['score_margin_2009'].fillna(0)
            for i in range(len(win_loss_df['map_Constituency_No'])):      
                margins_ae_score.append(user_input['weights']['margin_AE_weight']['recent_year']*(win_loss_df['score_margin_2018'][i])+user_input['weights']['margin_AE_weight']['mid_year']*(win_loss_df['score_margin_2014'][i])+user_input['weights']['margin_AE_weight']['initial_year']*(win_loss_df['score_margin_2009'][i]))
            win_loss_df['margins_ae_score']=margins_ae_score 

            win_loss_df['margins_score2']=user_input['weights']['margin_change_final_score_weight']['for_AC_score']*win_loss_df['margins_ac_score']+user_input['weights']['margin_change_final_score_weight']['for_AE_score']*win_loss_df['margins_ae_score']



            Vote_share_2018=datamap_df.merge(data_2018,left_on='map_Constituency_No', right_on='Constituency_No', how='left')
            Vote_share_2018=Vote_share_2018['VS%']
            win_loss_df['Vote_share_2018']=Vote_share_2018
            win_loss_df['Vote_share_2018-mean()']=win_loss_df['Vote_share_2018']-win_loss_df['Vote_share_2018'].mean()
            win_loss_df['std(Vote_share_2018)']=win_loss_df['Vote_share_2018'].std()
            win_loss_df['sigma(Vote_share_2018)']=win_loss_df['Vote_share_2018-mean()']/win_loss_df['std(Vote_share_2018)']
            Vote_shares_2018=[]
            for i in range(len(win_loss_df['map_Constituency_No'])):  
                if win_loss_df['sigma(Vote_share_2018)'][i]<-2:
                    Vote_shares_2018.append(0)
                elif win_loss_df['sigma(Vote_share_2018)'][i]<-1:
                    Vote_shares_2018.append(0.2)  
                elif win_loss_df['sigma(Vote_share_2018)'][i]<-0.5:
                    Vote_shares_2018.append(0.3)
                elif win_loss_df['sigma(Vote_share_2018)'][i]<0:
                    Vote_shares_2018.append(0.4)  
                elif win_loss_df['sigma(Vote_share_2018)'][i]>2:
                    Vote_shares_2018.append(1)
                elif win_loss_df['sigma(Vote_share_2018)'][i]>1:
                    Vote_shares_2018.append(0.8)
                elif win_loss_df['sigma(Vote_share_2018)'][i]>0.5:
                    Vote_shares_2018.append(0.6)
                elif win_loss_df['sigma(Vote_share_2018)'][i]>0:
                    Vote_shares_2018.append(0.5) 
                else:
                    Vote_shares_2018.append(np.nan)   # doubt
            win_loss_df['score_Vote_share_2018']=Vote_shares_2018   


            Vote_share_2014=datamap_df.merge(data_2014,left_on='map_Constituency_No', right_on='Constituency_No', how='left')
            Vote_share_2014=Vote_share_2014['VS%']
            win_loss_df['Vote_share_2014']=Vote_share_2014
            win_loss_df['Vote_share-mean()2014']=win_loss_df['Vote_share_2014']-win_loss_df['Vote_share_2014'].mean()
            win_loss_df['std(Vote_share)2014']=win_loss_df['Vote_share_2014'].std()
            win_loss_df['sigma(Vote_share)2014']=win_loss_df['Vote_share-mean()2014']/win_loss_df['std(Vote_share)2014']

            Vote_shares_2014=[]
            for i in range(len(win_loss_df['map_Constituency_No'])):
                if win_loss_df['sigma(Vote_share)2014'][i]<-2:
                    Vote_shares_2014.append(0)
                elif win_loss_df['sigma(Vote_share)2014'][i]<-1:
                    Vote_shares_2014.append(0.2)  
                elif win_loss_df['sigma(Vote_share)2014'][i]<-0.5:
                    Vote_shares_2014.append(0.3)
                elif win_loss_df['sigma(Vote_share)2014'][i]<0:
                    Vote_shares_2014.append(0.4)  
                elif win_loss_df['sigma(Vote_share)2014'][i]>2:
                    Vote_shares_2014.append(1)
                elif win_loss_df['sigma(Vote_share)2014'][i]>1:
                    Vote_shares_2014.append(0.8)
                elif win_loss_df['sigma(Vote_share)2014'][i]>0.5:
                    Vote_shares_2014.append(0.6)
                elif win_loss_df['sigma(Vote_share)2014'][i]>0:
                    Vote_shares_2014.append(0.5) 
                else:
                    Vote_shares_2014.append(np.nan)   # doubt
            win_loss_df['score_Vote_share_2014']=Vote_shares_2014 

            Vote_share_2009=datamap_df.merge(data_2009,left_on='map_Constituency_No', right_on='Constituency_No', how='left')
            Vote_share_2009=Vote_share_2009['VS%']
            win_loss_df['Vote_share_2009']=Vote_share_2009
            win_loss_df['Vote_share-mean()2009']=win_loss_df['Vote_share_2009']-win_loss_df['Vote_share_2009'].mean()
            win_loss_df['std(Vote_share)2009']=win_loss_df['Vote_share_2009'].std()
            win_loss_df['sigma(Vote_share)2009']=win_loss_df['Vote_share-mean()2009']/win_loss_df['std(Vote_share)2009']

            Vote_shares_2009=[]
            for i in range(len(win_loss_df['map_Constituency_No'])):  
                if win_loss_df['sigma(Vote_share)2009'][i]<-2:
                    Vote_shares_2009.append(0)
                elif win_loss_df['sigma(Vote_share)2009'][i]<-1:
                    Vote_shares_2009.append(0.2)  
                elif win_loss_df['sigma(Vote_share)2009'][i]<-0.5:
                    Vote_shares_2009.append(0.3)
                elif win_loss_df['sigma(Vote_share)2009'][i]<0:
                    Vote_shares_2009.append(0.4)  
                elif win_loss_df['sigma(Vote_share)2009'][i]>2:
                    Vote_shares_2009.append(1)
                elif win_loss_df['sigma(Vote_share)2009'][i]>1:
                    Vote_shares_2009.append(0.8)
                elif win_loss_df['sigma(Vote_share)2009'][i]>0.5:
                    Vote_shares_2009.append(0.6)
                elif win_loss_df['sigma(Vote_share)2009'][i]>0:
                    Vote_shares_2009.append(0.5) 
                else:
                    Vote_shares_2009.append(np.nan)   # doubt
            win_loss_df['score_Vote_share_2009']=Vote_shares_2009

            win_loss_df['ac_tolerance_Vote_share_2009_by_5%']=user_input['weights']['tolerance %']*abs(win_loss_df['Vote_share_2009'])

            Vote_shares_ac_score=[]                                       # error if condiction
            for i in range(len(win_loss_df['map_Constituency_No'])):   
                if win_loss_df['Vote_share_2018'][i]>(win_loss_df['ac_tolerance_Vote_share_2009_by_5%'][i])+(win_loss_df['Vote_share_2009'][i]):
                    Vote_shares_ac_score.append(1)
                elif win_loss_df['Vote_share_2018'][i]<=-(win_loss_df['ac_tolerance_Vote_share_2009_by_5%'][i])+(win_loss_df['Vote_share_2009'][i]):
                    Vote_shares_ac_score.append(0) 
                else:
                    Vote_shares_ac_score.append(0.5)   
            win_loss_df['Vote_shares_ac_score']=Vote_shares_ac_score
            Vote_shares_ae_score=[]
            win_loss_df['score_Vote_share_2018']=win_loss_df['score_Vote_share_2018'].fillna(0)
            win_loss_df['score_Vote_share_2014']=win_loss_df['score_Vote_share_2014'].fillna(0)
            win_loss_df['score_Vote_share_2009']=win_loss_df['score_Vote_share_2009'].fillna(0)
            for i in range(len(win_loss_df['map_Constituency_No'])):      
                Vote_shares_ae_score.append(user_input['weights']['vote_share_AE_weight']['recent_year']*(win_loss_df['score_Vote_share_2018'][i])+user_input['weights']['vote_share_AE_weight']['mid_year']*(win_loss_df['score_Vote_share_2014'][i])+user_input['weights']['vote_share_AE_weight']['initial_year']*(win_loss_df['score_Vote_share_2009'][i]))
            win_loss_df['Vote_shares_ae_score']=Vote_shares_ae_score 


            win_loss_df['Vote_shares_score2']=user_input['weights']['voteshare_change_final_score_weight']['for_AC_score']*win_loss_df['Vote_shares_ac_score']+user_input['weights']['voteshare_change_final_score_weight']['for_AE_score']*win_loss_df['Vote_shares_ae_score']


            win_loss_df['final_score']=user_input['weights']['net_score_weight']['for_winloss_AE_score']*win_loss_df['ae_score_winloss']+user_input['weights']['net_score_weight']['for_margin_final_score']*win_loss_df['margins_score2']+user_input['weights']['net_score_weight']['for_voteshare_final_score']*win_loss_df['Vote_shares_score2']+user_input['weights']['net_score_weight']['for_voteshare_AC_score']*win_loss_df['Vote_shares_ac_score']




            final_score_mean=win_loss_df['final_score'].mean()
            final_score_std=win_loss_df['final_score'].std()   
            category=[]
            for i in range(len(win_loss_df['map_Constituency_No'])):     
                if win_loss_df['final_score'][i]>=user_input['category_range']['safe']:
                    category.append('Safe')
                elif win_loss_df['final_score'][i]>=user_input['category_range']['Favorable']:
                    category.append('Favorable')
                
                elif win_loss_df['final_score'][i]<user_input['category_range']['Difficult']:
                    category.append('Difficult')
                else:
                    category.append('Battleground')                                                                                    
            
            win_loss_df['category']=category
            win_loss_df=win_loss_df.rename(columns={'Rank_2018':'rank_'+str(user_input['values']['initial_year3']),'Rank_2014':'rank_'+str(user_input['values']['initial_year2']),'Rank_2009':'rank_'+str(user_input['values']['initial_year1']),'score_margin_2018':'score_margin_'+str(user_input['values']['initial_year3']),'margin':'margin_'+str(user_input['values']['initial_year3']),'margin-mean(m)':'margin-mean()_'+str(user_input['values']['initial_year3']),'std(m)':'margin_std_'+str(user_input['values']['initial_year3']),'sigma(m)':'margin_sigma_'+str(user_input['values']['initial_year3']),'margin_2014':'margin_'+str(user_input['values']['initial_year2']),'margin-mean(m)2014':'margin-mean()_'+str(user_input['values']['initial_year2']),'std(m)2014':'margin_std_'+str(user_input['values']['initial_year2']),'sigma(m)2014':'margin_sigma_'+str(user_input['values']['initial_year2']),'score_margin_2014':'margin_score_'+str(user_input['values']['initial_year2']),'margin_2009':'margin_'+str(user_input['values']['initial_year1']),'margin-mean(m)2009':'margin-mean()_'+str(user_input['values']['initial_year1']),'std(m)2009':'margin_std_'+str(user_input['values']['initial_year1']),'sigma(m)2009':'margin_sigma_'+str(user_input['values']['initial_year1']),'score_margin_2009':'margin_score_'+str(user_input['values']['initial_year1']),'ac_tolerance_margin_2009_by_5%':'AC_tolerance_margin_'+str(user_input['values']['initial_year1'])+'_by_'+str(user_input['weights']['tolerance %']),'Vote_share_2018':'Vote_share_'+str(user_input['values']['initial_year3']),'Vote_share_2018-mean()':'Vote_share-mean()_'+str(user_input['values']['initial_year3']),'std(Vote_share_2018)':'Vote_share-std_'+str(user_input['values']['initial_year3']),'sigma(Vote_share_2018)':'Vote_share_sigma_'+str(user_input['values']['initial_year3']),'score_Vote_share_2018':'Vote_share_score_'+str(user_input['values']['initial_year3']),'Vote_share_2014':'Vote_share_'+str(user_input['values']['initial_year2']),'Vote_share-mean()2014':'Vote_share-mean()'+str(user_input['values']['initial_year2']),'std(Vote_share)2014':'Vote_share_std_'+str(user_input['values']['initial_year2']),'sigma(Vote_share)2014':'Vote_share_sigma_'+str(user_input['values']['initial_year2']),'score_Vote_share_2014':'Vote_share_score_'+str(user_input['values']['initial_year2']),'Vote_share_2009':'Vote_share_'+str(user_input['values']['initial_year1']),'Vote_share-mean()2009':'Vote_share_mean()_'+str(user_input['values']['initial_year1']),'std(Vote_share)2009':'Vote_share_std_'+str(user_input['values']['initial_year1']),'sigma(Vote_share)2009':'Vote_share_sigma_'+str(user_input['values']['initial_year1']),'score_Vote_share_2009':'Vote_share_score_'+str(user_input['values']['initial_year1']),'ac_tolerance_Vote_share_2009_by_5%':'AC_tolerance_Vote_share_'+str(user_input['values']['initial_year1'])+'_by_'+str(user_input['weights']['tolerance %'])})

            seat_classification_data=win_loss_df[['map_Constituency_No','final_score','category']]
            #seat_classification_data.to_excel("Seat_classification_"+data['Party'][2]+".xlsx")

            #win_loss_df.to_excel("Seat_classification_"+data['Party'][2]+"_with_all_attributes.xlsx")

            data_for_graph=pd.DataFrame(seat_classification_data['category'].value_counts(ascending=False))
            data_for_graph=data_for_graph.reset_index()
            data_for_graph=data_for_graph.rename(columns={'index':'Category','category':'Seats'})

            st.markdown('#')
            st.subheader("Seat Classification Data")
            st.write(seat_classification_data)
            @st.cache
            def convert_df(df):
              return df.to_csv().encode('utf-8')


            csv = convert_df(seat_classification_data)
            csv1 = convert_df(win_loss_df)

            st.download_button("Download",csv,"file.csv","text/csv",key='download-csv')

            st.download_button("Download All Attributes",csv1,"file.csv","text/csv",key='download-csv')
            
            st.markdown('#')
            st.subheader("Seat Classification Plot")
            
            import plotly.express as px
            
            fig_bar = px.bar(data_for_graph, x = "Category", y = "Seats",color='Category')
            fig_bar.update_layout(
                title="Seat Classification Plot for "+raw_data['Party'][0],
                xaxis_title="Category",
                yaxis_title="Seats",
                legend_title="Category")
            st.plotly_chart(fig_bar) 
            buffer = io.StringIO()
            fig_bar.write_html(buffer, include_plotlyjs='cdn')
            html_bytes = buffer.getvalue().encode()

            st.download_button(label='Download Seat Classification Plot',data=html_bytes,file_name='stuff.html',mime='text/html')        


    
 










        

        
    elif choice =="Sensitivity Graph":
        data_file1=st.file_uploader("upload file")
        st.write(data_file1)
        sen_df=pd.read_excel(data_file1,sheet_name = None)
        sheets=sen_df.keys()
        agree1 = st.multiselect('Sheet Names',sheets)
        #print(agree)
        sen_df1=pd.read_excel(data_file1,sheet_name = agree1[0])
        #st.dataframe(df1)
        cols=sen_df1.columns
        st.sidebar.subheader("Select Column Below")
        sen_state_Input=st.sidebar.selectbox("State",cols)
        sen_Year_Input=st.sidebar.selectbox("Year",cols)
        sen_Election_Type_Input=st.sidebar.selectbox("Election Type",cols)
        sen_Party_Input=st.sidebar.selectbox("Party",cols)
        sen_zone_Input=st.sidebar.selectbox("Zone",cols)
        sen_margin_Input=st.sidebar.selectbox("Margin %",cols)

        st.subheader("Give Values")
        sen_Party_Name_input=st.text_input("State Name")
        sen_recent_year2_input=st.text_input("Year")
        sen_Election_Type_value_input=st.text_input("Election Type")
        sen_recent_year1_input=st.text_input("Party")
        if st.checkbox('Run'):
            input={"file_name":data_file1,"sheet_name":agree1[0],"state":sen_Party_Name_input,"year":int(sen_recent_year2_input),"election_type":sen_Election_Type_value_input,"party":sen_recent_year1_input,"column_names":{"state":sen_state_Input,"year":sen_Year_Input,"election_type":sen_Election_Type_Input,"party":sen_Party_Input,"zone":sen_zone_Input,"margin":sen_margin_Input}}
            #input={"file_name":"D:/New folder/RJ/new/sensitivity graph QC (1).xlsx","sheet_name":"Data","state":"Telangana","year":2018,"election_type":"AE","party":"INC","column_names":{"state":"State","year":"YEAR","election_type":"Election Type","party":"Party Name","zone":"Zone","margin":"Margin (%)"}}


            data=pd.read_excel(input['file_name'],sheet_name=input['sheet_name'])

            data=data[data[input['column_names']['state']]==input['state']]
            data=data[data[input['column_names']['year']]==input['year']]
            data=data[data[input['column_names']['election_type']]==input['election_type']]
            data=data[data[input['column_names']['party']]==input['party']]
            data=data[[input['column_names']['state'],input['column_names']['year'],input['column_names']['election_type'],input['column_names']['party'],input['column_names']['margin'],input['column_names']['zone']]]
            data=data.rename(columns={input['column_names']['zone']:"Zone",input['column_names']['margin']:"Margin (%)"}) 


            zone=data['Zone'].unique()
            zone_data=[]
            positive_data=[]
            negative_data=[]
            for i in zone:       
                data_zone=data[data['Zone']==i]
                data_zone1=data_zone['Margin (%)']
                data_zone2=data_zone1.to_list()
                data_zone2.sort()
                data_zone2.insert(data_zone2.index(min([i for i in data_zone2 if i > 0])),0)
                negative=data_zone2[:data_zone2.index(0)+1]
                positive=data_zone2[data_zone2.index(0)+1:]
                positive.insert(0,i)
                negative.insert(0,i)
                positive_data.append(positive)
                negative_data.append(negative)             
                
            # positive and negative df:

            positive_df=pd.DataFrame(positive_data)
            negative_df=pd.DataFrame(negative_data)

            # transposing df:

            positive_df=positive_df.T
            negative_df=negative_df.T

            # convert first row to column headers.
            new_header = positive_df.iloc[0] 
            positive_df = positive_df[1:] 
            positive_df.columns = new_header

            new_headers = negative_df.iloc[0] 
            negative_df = negative_df[1:] 
            negative_df.columns = new_headers
            negative_df=negative_df.fillna(-600)

            # negative 1
            n=negative_df.columns
            negative_data1=[]
            for i in n:      
                negative_list=negative_df[i].sort_values().to_list()
                negative_list.insert(0,i)
                negative_data1.append(negative_list)            
            
            # negative1 transpose:
            negative_df1=pd.DataFrame(negative_data1)
            negative_df1=negative_df1.T

            # convert first row to column headers.
            new_headerss = negative_df1.iloc[0] 
            negative_df1 = negative_df1[1:] 
            negative_df1.columns = new_headerss

            # compute rank column:
            positive_df['rank']=list(range(1,len(positive_df)+1,1))
            negative_df1['rank']=list(range(-len(negative_df1)+1,1,1))


            zone_df=pd.concat([negative_df1, positive_df],ignore_index=True)
            zone_df = zone_df.replace(-600,np.nan)



            # max list and min list:

            max_list=[]
            min_list=[]
            for i in zone_df.columns:   
                max_list.append(math.ceil(zone_df[i].max()))
                min_list.append(math.floor(zone_df[i].min()))            
            # min range and max range :


            if max(max_list)>abs(min(min_list)):
               range_value=max(max_list)
            else:
               range_value=abs(min(min_list))    

            range_value=5*round(range_value/5)
            margin=list(range(-range_value,range_value+1,5))

            # convert margin list to df:

            margin_df=pd.DataFrame(margin,columns=['margin'])


            # Zone df:


            distinct_zone=pd.DataFrame(data['Zone'].unique(),columns=['zone'])

            # creating key column for cross join:

            distinct_zone['key']=1
            margin_df['key']=1

            # perform cross join:
            margin_zone_df=pd.merge(margin_df, distinct_zone, on ='key').drop("key", 1)

            # finalize limits, lower and upper values:

            for i in range(len(margin_zone_df)):   
                z=margin_zone_df.loc[i,'zone']
                m=margin_zone_df.loc[i,'margin']
                z_df=zone_df[z]
                z_df=z_df.dropna()
                min_margin=min(z_df)     # minimum margin
                max_margin=max(z_df)     # maximum margin
                max_margin=math.ceil(max_margin/5)*5   # round the maximum margin to nearest 5.
                min_margin=math.floor(min_margin/5)*5  # round the minimum margin to nearest 5. 
                if m>=min_margin and m<=max_margin:  
                    tem_df=zone_df[z]    
                    if m<0:
                       tem_df=tem_df[tem_df>=m]
                       low_margin=min(tem_df)
                       rank_df=zone_df[[z,'rank']]
                       rank_df=rank_df[rank_df[z]==low_margin]
                       rank_df.reset_index(inplace = True)
                       rnk=rank_df['rank'][0]
                    elif m>0:
                       tem_df=tem_df[tem_df<=m]
                       high_margin=max(tem_df)
                       rank_df=zone_df[[z,'rank']]
                       rank_df=rank_df[rank_df[z]==high_margin]
                       rank_df.reset_index(inplace = True)
                       rnk=rank_df['rank'][0]
                    elif m==0:
                       rnk=0    
                    margin_zone_df.loc[i,'rank']=rnk   # computing rank or seats.
            # pivote to get final table:

            final_graph_data=margin_zone_df.pivot(index='margin', columns='zone', values='rank')
            # rest index:
            final_graph_data.reset_index(inplace = True)

            # Plot in plotly dynamic:
            st.subheader("Sensitivity Plot")
            import plotly.express as px

            df = px.data.gapminder().query("continent=='Oceania'")
            fig = px.line(final_graph_data, x="margin", y=final_graph_data.columns[1:])
            #fig = px.line(final_graph_data, x="margin", y='Bombay Karnataka')
            fig.add_hline(y=0,line_width=2, line_color="black")
            #fig.add_vrect(x1=0)
            fig.add_vline(x=0, line_width=2, line_color="black")     

            fig.update_layout(
                title="Sensitivity graph for "+data[data.columns[0]][0],
                xaxis_title="Margin",
                yaxis_title="Rank or Seats",
                legend_title="Zones")
            st.plotly_chart(fig)
            #fig.write_image("/content/sample_data/sensitivity_plot.png")
            #fig.write_html(data[data.columns[0]][0]+" Sensitivity_plot.html")     
            buffer = io.StringIO()
            fig.write_html(buffer, include_plotlyjs='cdn')
            html_bytes = buffer.getvalue().encode()

            st.download_button(label='Download Sensitivity Plot',data=html_bytes,file_name='stuff.html',mime='text/html')        
                                                                        
            st.markdown('#')
            st.subheader("Sensitivity Plot Data")
            st.write(final_graph_data)
            @st.cache
            def convert_df(df):
                return df.to_csv().encode('utf-8')


            sen_csv = convert_df(final_graph_data)

            st.download_button("Download",sen_csv,"file.csv","text/csv",key='download-csv')


        



    elif choice=="file":
        st.subheader("file")

    else:
        st.subheader("no")   

    #data=pd.read_excel(data_file)
    #columns=data.columns
    #cho=st.sidebar.selectbox("Menu",columns)



if __name__ == '__main__':
    main()        


  
