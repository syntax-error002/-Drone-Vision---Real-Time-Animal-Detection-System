import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { Camera, Zap } from 'lucide-react-native';

export default function HomeScreen() {
    const router = useRouter();

    return (
        <View style={styles.container}>
            <View style={styles.content}>
                <View style={styles.iconContainer}>
                    <Zap size={64} color="#00f3ff" />
                </View>
                <Text style={styles.title}>Drone Vision</Text>
                <Text style={styles.subtitle}>AI-Powered Object Detection</Text>

                <TouchableOpacity
                    style={styles.button}
                    onPress={() => router.push('/camera')}
                    activeOpacity={0.8}
                >
                    <Camera size={24} color="#00f3ff" style={styles.btnIcon} />
                    <Text style={styles.btnText}>INITIATE SCAN</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#050505',
        alignItems: 'center',
        justifyContent: 'center',
    },
    content: {
        alignItems: 'center',
        width: '100%',
        paddingHorizontal: 20,
    },
    iconContainer: {
        marginBottom: 40,
        borderWidth: 2,
        borderColor: '#00f3ff',
        borderRadius: 20,
        padding: 20,
        backgroundColor: 'rgba(0, 243, 255, 0.1)',
        shadowColor: '#00f3ff',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.8,
        shadowRadius: 20,
        elevation: 10,
    },
    title: {
        fontSize: 36,
        fontWeight: '900',
        color: '#fff',
        letterSpacing: 4,
        marginBottom: 4,
        textTransform: 'uppercase',
    },
    subtitle: {
        fontSize: 14,
        color: '#00f3ff',
        marginBottom: 60,
        letterSpacing: 2,
        fontStyle: 'italic',
    },
    button: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(0, 243, 255, 0.15)',
        paddingVertical: 18,
        paddingHorizontal: 40,
        borderRadius: 4,
        borderWidth: 1,
        borderColor: '#00f3ff',
        shadowColor: '#00f3ff',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.5,
        shadowRadius: 15,
    },
    btnIcon: {
        marginRight: 12,
    },
    btnText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#00f3ff',
        textTransform: 'uppercase',
        letterSpacing: 2,
    },
});
