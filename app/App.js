
import * as React from 'react';
import { View, Text, TextInput, ScrollView, StyleSheet, Image, ImageBackground, Button, TouchableOpacity } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import Card from './components/card';
import CaroselCard from './components/caroselcard';



class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loggedIn: null,
      username: null,
      password: null,
      day: null,
      hour: null,
      eventName: null,
      eventDesc: null,
      "dogName": null,
      "dogAge": null,
      "dogBio": null,

      dogs: []
    }
  }



  HomeScreenCardHelper = (navigate) => {
    let returnVal = this.state.dogs.map((dog) => {
      return (
        <Card title={dog.dogName} content={dog.dogBio} callback={() => {
          navigate('Profile', { data: dog })
        }} />
      );
    })
    return returnVal;
  }

  CaroselCardHelper = (routeData) => {
    let cardList = routeData.dogSchedule.map((eventVar) => {
      return (<CaroselCard day={eventVar.day} time={eventVar.time} name={eventVar.eventName} desc={eventVar.eventDesc} />);
    });
    return cardList;
  }

  Profile = ({ navigation, route }) => {
    let styles = StyleSheet.create({
      parentWrapper: {

        backgroundColor: '#45C3D6',

        flex: 1

      },
      main: {
        justifyContent: 'space-between',
        alignItems: 'center',
        flex: 1
      },
      secondary: {

      },
      imagePFP: {
        alignContent: 'stretch',
        height: 250
      },
      descFont: {
        fontSize: 20,
        color: 'white'
      },
      mainWrapper: {
        flexDirection: 'column',
        flex: 1,

      },
      calendarWrapper: {
        flex: 1,
      },
      calendarHead: {
        backgroundColor: '#375459',
        flexDirection: 'row',
        alignContent: 'center',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 10
      },
      scheduleText: {
        color: 'white',
        padding: 10,
      },
      profileWrapper: {
        padding: 10,
        backgroundColor: '#45C3D6',
        flex: 1
      },
      DogName: {
        fontWeight: '700',
        fontSize: 25,
        marginBottom: 5,
        color: 'white'
      },
      DogAge: {
        fontSize: 15,
        marginBottom: 5,
        color: 'white'
      }
    })

    if (route.params.data) {
      let routeData = route.params.data;
      return (
        <View style={styles.mainWrapper}>

          <View style={styles.parentWrapper}>
            <ScrollView>
              <View style={styles.main}>
                <View style={styles.secondary}>
                  <Image style={styles.imagePFP} resizeMode="contain" source={require('./assets/fidoinfieldhighres.jpg')} />
                </View>
              </View>
              <View style={styles.profileWrapper}>
                <Text style={styles.descFont, styles.DogName}>{routeData.dogName}</Text>
                <Text style={styles.descFont, styles.DogAge}>{routeData.dogAge} Years Old</Text>
                <Text style={styles.descFont}>{routeData.dogBio}</Text>
              </View>
            </ScrollView>
          </View>

          <View style={styles.calendarWrapper}>
            <View style={styles.calendarHead}>
              <Text style={styles.scheduleText}>Schedule</Text>
              <TouchableOpacity onPress={() => {
                navigation.navigate('Event');
              }}><Text style={{ color: 'white', fontSize: 25 }}>+</Text></TouchableOpacity>
            </View>
            <ScrollView horizontal={true}>
              {this.CaroselCardHelper(routeData)}
            </ScrollView>
          </View>

        </View>

      );
    }
    else {
      return (<View><Text></Text></View>);
    }



  }

  Register = ({ navigation: { navigate } }) => {
    return (
      <View style={{ padding: 30 }}>
        <Text style={{ fontSize: 35, marginBottom: 25 }}>Register Dog</Text>
        <Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >dog name</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ dogName: text })}
          value={this.state.dogName}
        />
        <Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >dog age</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ dogAge: text })}
          value={this.state.dogAge}
        />
        <Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >dog bio</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ dogBio: text })}
          value={this.state.dogBio}
        />

        <TouchableOpacity style={{
          backgroundColor: '#45C3D6',
          paddingHorizontal: 20,
          paddingVertical: 10,
          borderRadius: 5,
          marginTop: 30,

        }}
          onPress={() => {
            //CODE HERE FOR POSTING UP REGISTRATION
            fetch('http://ec2-35-171-9-33.compute-1.amazonaws.com:5000/registerdog', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              mode: 'cors',
              body: JSON.stringify({
                "username": this.state.username,
                "password": this.state.password,
                "dogName": this.state.dogName,
                "dogAge": this.state.dogAge,
                "dogBio": this.state.dogBio,
                "dogSchedule": []
              })
            }).then(res => res.json()).then(res => {


              this.setState({ loggedIn: false });
              this.setState({ dogs: null })

            }).catch().finally(() => {
              fetch('http://ec2-35-171-9-33.compute-1.amazonaws.com:5000/snapshot', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                mode: 'cors',
                body: JSON.stringify({ "username": this.state.username, "password": this.state.password })
              }).then(res => res.json()).then(res => {
                console.log(res);
                if (res.success) {
                  navigate('Home')

                }
              }).catch();
            });

          }}

        >
          <View>
            <Text style={{ fontSize: 25, color: 'white' }}>Send To Server</Text>
          </View>
        </TouchableOpacity>

      </View>
    );
  }

  RegisterEvent = ({ navigation: { navigate } }) => {
    return (
      <ScrollView>
      <View style={{ padding: 30 }}>
        <Text style={{ fontSize: 35, marginBottom: 25 }}>Schedule Event</Text>
        <Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >dog name</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ dogName: text })}
          value={this.state.dogName}
        />
        <Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >day</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ day: text })}
          value={this.state.day}
        />
        <Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >hour</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ hour: text })}
          value={this.state.hour}
        />

        <Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >event name</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ eventName: text })}
          value={this.state.eventName}
        />

<Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >event description</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ eventDesc: text })}
          value={this.state.eventDesc}
        />

        <TouchableOpacity style={{
          backgroundColor: '#45C3D6',
          paddingHorizontal: 20,
          paddingVertical: 10,
          borderRadius: 5,
          marginTop: 30,

        }}
          onPress={() => {
            //CODE HERE FOR POSTING UP REGISTRATION
            fetch('http://ec2-35-171-9-33.compute-1.amazonaws.com:5000/scheduledog', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              mode: 'cors',
              body: JSON.stringify({
                "username": this.state.username,
                "password": this.state.password,
                "dogName": this.state.dogName,
                "day": parseInt(this.state.day),
                "hour": parseInt(this.state.hour),
                "eventName": this.state.eventName,
                "eventDesc": this.state.eventDesc
              })
            }).then(res => res.json()).then(res => {


              this.setState({ loggedIn: false });
              this.setState({ dogs: null })

            }).catch().finally(() => {
              fetch('http://ec2-35-171-9-33.compute-1.amazonaws.com:5000/snapshot', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                mode: 'cors',
                body: JSON.stringify({ "username": this.state.username, "password": this.state.password })
              }).then(res => res.json()).then(res => {
                console.log(res);
                if (res.success) {
                  navigate('Home')

                }
              }).catch();
            });

          }}

        >
          <View>
            <Text style={{ fontSize: 25, color: 'white' }}>Send To Server</Text>
          </View>
        </TouchableOpacity>

      </View>
      </ScrollView>
    );
  }


  Logo = () => {
    return (<Image resizeMode="contain" style={{ width: 100, height: 100 }} source={require('./assets/inverselogo.png')} />)
  }



  HomeScreenCards = ({ navigation: { navigate } }) => {


    return (
      <View style={{
        flex: 1,
        flexDirection: "column"
      }}>
        <ImageBackground source={require('./assets/appbottomdesign.jpg')} style={{
          flex: 1,
          resizeMode: "cover",
          justifyContent: "center"
        }}>
          <ScrollView>
            {this.HomeScreenCardHelper(navigate)}
          </ScrollView>

        </ImageBackground>
      </View>
    );
  }


  HomeScreen = ({ navigation: { navigate } }) => {

    return (
      <View style={{ padding: 30 }}>
        <Text style={{ fontSize: 35, marginBottom: 25 }}>Login</Text>
        <Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >username</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ username: text })}
          value={this.state.username}
        />
        <Text
          style={{ fontSize: 25, paddingBottom: 15, paddingTop: 15 }}
        >password</Text>
        <TextInput style={{ borderColor: 'grey', borderWidth: 1, padding: 5 }}
          onChangeText={(text) => this.setState({ password: text })}
          value={this.state.password}
        />


        <TouchableOpacity style={{
          backgroundColor: '#45C3D6',
          paddingHorizontal: 20,
          paddingVertical: 10,
          borderRadius: 5,
          marginTop: 30,

        }}
          onPress={() => {
            fetch('http://ec2-35-171-9-33.compute-1.amazonaws.com:5000/login', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              mode: 'cors',
              body: JSON.stringify({ "username": this.state.username, "password": this.state.password })
            }).then(res => res.json()).then(res => {
              if (res.success) {

              }
            }).catch();

            fetch('http://ec2-35-171-9-33.compute-1.amazonaws.com:5000/snapshot', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              mode: 'cors',
              body: JSON.stringify({ "username": this.state.username, "password": this.state.password })
            }).then(res => res.json()).then(res => {
              console.log(res);
              if (res.success) {
                this.setState({ loggedIn: true });
                this.setState({ dogs: res.data });
                navigate('Home')
              }
            }).catch();


            //CODE HERE FOR POSTING UP Login for simplicities sake this will treat as if it worked

          }}

        >
          <View>
            <Text style={{ fontSize: 25, color: 'white' }}>Send To Server</Text>
          </View>
        </TouchableOpacity>

      </View>
    );


  }



  render() {
    const Stack = createStackNavigator();
    return (
      <NavigationContainer>
        <Stack.Navigator screenOptions={{
          headerStyle: {
            backgroundColor: '#45C3D6',
            height: 130
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          headerTitle: props => <this.Logo />,


        }}>
          <Stack.Screen name="Login" component={this.HomeScreen} />
          <Stack.Screen name="Home" component={this.HomeScreenCards} options={this.state.loggedIn ? ({ route, navigation }) => ({

            headerRight: () => (

              <TouchableOpacity onPress={() => navigation.navigate('Register')} style={{
                padding: 30
              }}>
                <Text style={{ color: 'white', fontSize: 30 }}>+</Text>
              </TouchableOpacity>
            ),

          }) : <View></View>} />
          <Stack.Screen name="Profile" component={this.Profile} />
          <Stack.Screen name="Register" component={this.Register} />
          <Stack.Screen name="Event" component={this.RegisterEvent} />

        </Stack.Navigator>
      </NavigationContainer>
    );
  }
}

export default App;