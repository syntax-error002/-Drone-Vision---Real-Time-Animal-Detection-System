import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function Layout() {
    return (
        <>
            <StatusBar style="light" />
            <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#0f172a' } }}>
                <Stack.Screen name="index" />
                <Stack.Screen name="camera" options={{ animation: 'slide_from_right' }} />
            </Stack>
        </>
    );
}
