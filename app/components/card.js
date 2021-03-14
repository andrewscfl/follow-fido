import React from 'react';
import { StyleSheet, Text, View, Button, Image, TouchableOpacity } from 'react-native';

const Card = (props) => {
    return (
        <TouchableOpacity onPress={props.callback}>
            <View style={cardStyles.CardContainerParent}>
                <View style={cardStyles.CardContainer}>
                    <View style={cardStyles.CardImg}>
                    <Image style={{width: 70, height: 70}} resizeMode="contain" source={require('../assets/headshoticon.jpg')} />
                    </View>
                    <View style={cardStyles.CardBody}>
                        <Text style={cardStyles.Title}>{props.title}</Text>
                        <Text>{props.content}</Text>
                    </View>
                </View>
                
            </View>
        </TouchableOpacity>
    );
}

const cardStyles = StyleSheet.create({
    CardContainerParent: {
        borderBottomColor: '#f2f2f2',
        borderBottomWidth: 1,
        marginTop:5,
        marginHorizontal: 5,
        padding: 15,
        backgroundColor: "white"
    },
    CardContainer: {
        display: 'flex',
        flexDirection: 'row',
    },
    CardImg: {
        flex: 1
    },
    CardBody: {
        flex: 3,
        paddingLeft: 20
    },
    Title: {
        fontSize: 20
    }
});


export default Card;