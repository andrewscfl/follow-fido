import React from 'react';
import { StyleSheet, Text, View, Button, Image, TouchableOpacity } from 'react-native';

const CaroselCard = (props) => {
    console.log(props.day);
    console.log(props.time);

    let Time = props.time;

        let response = "";
        switch(props.day){
            case 1:
                response += 'Monday';
                break;
            case 2:
                response+= 'Tuesday';
                break;
            case 3:
                response+='Wednsday';
                break;
            case 4:
                response+='Thursday';
                break;
            case 5:
                response+='Friday';
                break;
            case 6:
                response+='Saturday';
                break;
            case 7:
                response+='Sunday';
                break;
            default:
                break;

        }

       
            let stringTime = Time.toString();
            let milTime = stringTime.substr(0,2) + ":" + stringTime.substr(2,5);

            response += " at \n" + milTime;

            console.log(response);
            
              

    
    
    console.log(response);
    return (
        <View style={caroStyles.card}>
            <Text style={caroStyles.cardTitle}>{props.name}</Text>
            <Text style={caroStyles.cardBody}>{props.desc}</Text>
            <Text style={caroStyles.cardTime}>{response}</Text>
        </View>
    );
}

const caroStyles = StyleSheet.create({
   card : {
       backgroundColor: '#45C3D6',
       padding: 20,
       borderRadius: 30,
       margin:10,
       width: 300

   },
   cardTitle: {
       color: 'white',
       fontSize: 25,
       marginBottom: 15
   },
   cardBody:{
       color: 'white',
       fontSize: 20,
       marginBottom: 15
   },
   cardTime: {
       fontSize: 35,
       color: 'white'
   }
});


export default CaroselCard;