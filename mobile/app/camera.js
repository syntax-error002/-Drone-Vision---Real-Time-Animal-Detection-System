import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, Switch, Animated, Easing, SafeAreaView, Platform, StatusBar, Dimensions } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useRouter } from 'expo-router';
import { ArrowLeft, Scan, Flashlight, ZoomIn, ZoomOut, Radio, Zap } from 'lucide-react-native';
import { useState, useRef, useEffect } from 'react';
import * as Haptics from 'expo-haptics';
import * as Speech from 'expo-speech';

// Configure API URL - Update this to match your server
// Using localhost because ADB reverse tethering is active (USB Debugging)
const API_URL = 'http://127.0.0.1:5000';
const PREDICT_ENDPOINT = `${API_URL}/predict`;
const STREAM_ENDPOINT = `${API_URL}/stream`;

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// Bounding Box Component
const BoundingBox = ({ bbox, label, color = '#00f3ff' }) => {
    // bbox is [x1, y1, x2, y2] from YOLO (relative to image, needs scaling)
    // We'll trust the parent to pass scaled coordinates or handling responsive scaling

    const opacity = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        Animated.sequence([
            Animated.timing(opacity, { toValue: 1, duration: 200, useNativeDriver: true }),
            Animated.delay(1000),
            Animated.timing(opacity, { toValue: 0.5, duration: 500, useNativeDriver: true })
        ]).start();
    }, [bbox]);

    if (!bbox) return null;

    const [x1, y1, x2, y2] = bbox;
    const width = Math.abs(x2 - x1);
    const height = Math.abs(y2 - y1);

    return (
        <Animated.View style={[styles.bbox, {
            left: x1,
            top: y1,
            width: width,
            height: height,
            borderColor: color,
            opacity
        }]}>
            <View style={[styles.bboxLabel, { backgroundColor: color }]}>
                <Text style={styles.bboxText}>{label}</Text>
            </View>
            <View style={styles.cornerTL} />
            <View style={styles.cornerTR} />
            <View style={styles.cornerBL} />
            <View style={styles.cornerBR} />
        </Animated.View>
    );
};

export default function CameraScreen() {
    const [permission, requestPermission] = useCameraPermissions();
    const router = useRouter();
    const cameraRef = useRef(null);

    // State
    const [scanning, setScanning] = useState(false);
    const [result, setResult] = useState(null);
    const [isAutoScan, setIsAutoScan] = useState(false);
    const [isConnected, setIsConnected] = useState(true);

    // New Feature State
    const [zoom, setZoom] = useState(0); // 0 to 1
    const [torch, setTorch] = useState(false);
    const [logs, setLogs] = useState(["SYSTEM INITIALIZED...", "SENSORS ONLINE"]); // Data Stream Logs
    const [frameCounter, setFrameCounter] = useState(0);
    const [fps, setFps] = useState(0);

    // Dynamic Bounding Box State
    const [activeBox, setActiveBox] = useState(null); // { bbox: [x,y,w,h], label: "..." }

    // Animation
    const scanLineAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        if (scanning) {
            Animated.loop(
                Animated.sequence([
                    Animated.timing(scanLineAnim, {
                        toValue: 1, duration: 1500, easing: Easing.linear, useNativeDriver: true
                    }),
                    Animated.timing(scanLineAnim, {
                        toValue: 0, duration: 0, useNativeDriver: true
                    })
                ])
            ).start();
        } else {
            scanLineAnim.setValue(0);
        }
    }, [scanning]);

    const speak = (text) => {
        Speech.stop();
        Speech.speak(text, {
            language: 'en',
            pitch: 0.8, // Lower pitch for "Jarvis" feel
            rate: 0.9,
        });
    };

    const addLog = (text) => {
        setLogs(prev => [text, ...prev].slice(0, 6)); // Keep last 6 logs
    };

    const processFrame = async (isManualScan = false) => {
        if (!cameraRef.current) return;
        if (scanning && !isAutoScan) return; // Allow concurrent processing in auto-scan mode

        try {
            setScanning(true);
            if (isManualScan) setResult(null);

            // Audio & Haptic Feedback - "Scanning"
            if (isManualScan) {
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            }

            const startTime = Date.now();

            // 1. Capture (Optimized for real-time)
            // Removed skipProcessing and slightly reduced quality for speed
            const photo = await cameraRef.current.takePictureAsync({
                quality: isAutoScan ? 0.5 : 0.8,
                base64: false,
                imageType: 'jpg',
                scale: isAutoScan ? 0.5 : 1.0,
            });

            // Calculate scale factors for "cover" mode (Aspect Fill)
            // The preview typically fills the screen, cropping the "overflow" dimensions.
            const scale = Math.max(SCREEN_WIDTH / photo.width, SCREEN_HEIGHT / photo.height);
            const scaledWidth = photo.width * scale;
            const scaledHeight = photo.height * scale;

            // Calculate offsets (centering the image)
            const offsetX = (SCREEN_WIDTH - scaledWidth) / 2;
            const offsetY = (SCREEN_HEIGHT - scaledHeight) / 2;

            // 2. Prepare form data
            const formData = new FormData();
            const fileName = isAutoScan ? 'frame.jpg' : 'scan.jpg';
            formData.append('file', {
                uri: photo.uri,
                name: fileName,
                type: 'image/jpeg'
            });

            // For streaming endpoint, include frame index
            if (isAutoScan) {
                formData.append('frame_idx', frameCounter.toString());
            }

            // 3. Send to appropriate endpoint
            const endpoint = isAutoScan ? STREAM_ENDPOINT : PREDICT_ENDPOINT;
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), isAutoScan ? 5000 : 15000);

            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData,
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                signal: controller.signal,
            });
            clearTimeout(timeoutId);

            if (!response.ok) throw new Error(`Status: ${response.status}`);

            setIsConnected(true);
            const data = await response.json();

            // Handle skipped frames in streaming mode
            if (data.skipped) {
                setScanning(false);
                setFrameCounter(prev => prev + 1);
                return;
            }

            // Calculate FPS for real-time mode
            if (isAutoScan && data.metrics?.fps) {
                setFps(data.metrics.fps);
                addLog(`FPS: ${data.metrics.fps.toFixed(1)}`);
            }

            // Show result & Update Bounding Box
            const match = data.best_match;
            if (match) {
                setResult(match);

                // Process Bounding Box
                // YOLO returns [x1, y1, x2, y2]
                if (match.bbox) {
                    const [bx1, by1, bx2, by2] = match.bbox;
                    const scaledBox = [
                        bx1 * scale + offsetX,
                        by1 * scale + offsetY,
                        bx2 * scale + offsetX,
                        by2 * scale + offsetY
                    ];
                    setActiveBox({ bbox: scaledBox, label: match.label });
                }

                // "Target Confirmed" Feedback
                Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
                if (isManualScan || (isAutoScan && Math.random() > 0.9)) {
                    speak(`Target Confirmed. ${match.label}`);
                }
                if (isAutoScan) {
                    addLog(`DETECTED: ${match.label.toUpperCase()}`);
                }
            } else {
                setResult({ label: 'No Match', details: { emoji: '🤔', fact: 'Sensors calibrating...' } });
                setActiveBox(null);
            }

            // Update frame counter
            if (isAutoScan) {
                setFrameCounter(prev => prev + 1);
            }

            // Update performance log
            const processingTime = Date.now() - startTime;
            if (isAutoScan && processingTime < 100) {
                addLog(`PROCESSING: ${processingTime}ms`);
            }

        } catch (error) {
            console.log("Scan Error:", error.message);
            setIsConnected(false);
            addLog(`ERROR: ${error.message.substring(0, 20)}`);
            if (isManualScan) {
                Alert.alert("Connection Error", `Unable to connect to server.\n\nPlease check:\n- Server is running\n- IP address: ${API_URL}\n- Network connection`);
            }
        } finally {
            setScanning(false);
        }
    };

    // Real-Time Auto Scan Loop with optimized timing
    useEffect(() => {
        let isActive = true;
        let lastFrameTime = 0;
        const targetInterval = 1000 / 15; // Target 15 FPS for real-time

        const loop = async () => {
            if (!isActive || !isAutoScan) {
                setScanning(false);
                return;
            }

            const now = Date.now();
            const elapsed = now - lastFrameTime;

            // Adaptive timing: adjust interval based on actual processing time
            const delay = Math.max(0, targetInterval - elapsed);

            await processFrame(false);

            lastFrameTime = Date.now();

            // Continue loop with adaptive delay for consistent FPS
            if (isActive && isAutoScan) {
                setTimeout(loop, delay);
            }
        };

        if (isAutoScan) {
            lastFrameTime = Date.now();
            loop();
            addLog("AUTO-SCAN ENABLED");
        } else {
            addLog("MANUAL MODE");
            setActiveBox(null);
        }

        return () => {
            isActive = false;
        };
    }, [isAutoScan]);


    if (!permission) return <View />;
    if (!permission.granted) {
        return (
            <View style={styles.container}>
                <Text style={styles.message}>Camera permission needed</Text>
                <TouchableOpacity onPress={requestPermission} style={styles.button}>
                    <Text style={styles.text}>Grant Permission</Text>
                </TouchableOpacity>
            </View>
        );
    }

    const translateY = scanLineAnim.interpolate({
        inputRange: [0, 1],
        outputRange: [0, 600] // Extended range for larger screens
    });

    // Cinematic Components
    const CornerBrackets = () => (
        <View style={StyleSheet.absoluteFill} pointerEvents="none">
            <View style={[styles.corner, styles.tl]} />
            <View style={[styles.corner, styles.tr]} />
            <View style={[styles.corner, styles.bl]} />
            <View style={[styles.corner, styles.br]} />
        </View>
    );

    const DataStream = () => (
        <View style={styles.dataStreamContainer} pointerEvents="none">
            {logs.map((log, i) => (
                <Text key={i} style={[styles.logText, { opacity: 1 - (i * 0.15) }]}>
                    {`> ${log}`}
                </Text>
            ))}
        </View>
    );

    const handleZoom = (increment) => {
        setZoom(prev => {
            const newZoom = Math.max(0, Math.min(1, prev + increment));
            Haptics.selectionAsync();
            return newZoom;
        });
    };

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="light-content" />
            <CameraView
                ref={cameraRef}
                style={StyleSheet.absoluteFill}
                facing="back"
                animateShutter={false}
                zoom={zoom}
                enableTorch={torch}
            />

            {/* Dynamic Bounding Box Layer */}
            {activeBox && (
                <BoundingBox
                    bbox={activeBox.bbox}
                    label={activeBox.label}
                />
            )}

            <View style={styles.overlay}>
                <CornerBrackets />
                <DataStream />

                {/* 1. Top HUD Bar */}
                <View style={styles.topHud}>
                    <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
                        <ArrowLeft size={20} color="#00f3ff" />
                    </TouchableOpacity>

                    <View style={styles.statusDisplay}>
                        <View style={[styles.statusDot, { backgroundColor: isConnected ? '#00f3ff' : '#ef4444' }]} />
                        <Text style={styles.statusText}>
                            {isConnected ? (isAutoScan && fps > 0 ? `${fps.toFixed(0)} FPS` : "SYSTEM ONLINE") : "OFFLINE"}
                        </Text>
                    </View>

                    <View style={styles.topRightDecoration} />
                </View>

                {/* 2. Main Content Area */}
                <View style={styles.mainArea}>

                    {/* Left: Result Hologram (Appears when needed) */}
                    <View style={styles.resultZone}>
                        {result && (
                            <View style={styles.resultCard}>
                                <View style={styles.cardHeader}>
                                    <Text style={styles.emoji}>{result.details?.emoji || 'null'}</Text>
                                    <View>
                                        <Text style={styles.animalTitle}>{result.label.toUpperCase()}</Text>
                                        <Text style={styles.confidenceText}>INTEGRITY: {(result.confidence * 100).toFixed(0)}%</Text>
                                    </View>
                                </View>
                                <View style={styles.divider} />
                                <View style={styles.statsGrid}>
                                    <View style={styles.statItem}>
                                        <Text style={styles.statLabel}>DIET</Text>
                                        <Text style={styles.statValue}>{result.details?.diet || 'N/A'}</Text>
                                    </View>
                                    <View style={styles.statItem}>
                                        <Text style={styles.statLabel}>SPEED</Text>
                                        <Text style={styles.statValue}>{result.details?.speed || 'N/A'}</Text>
                                    </View>
                                </View>
                                <Text style={styles.factText}>{result.details?.fact || 'analyzing...'}</Text>
                            </View>
                        )}
                    </View>

                    {/* Center: Scanner Reticle - Only show in manual mode or when searching */}
                    <View style={styles.reticleZone}>
                        {scanning && !activeBox && (
                            <>
                                <Animated.View style={[styles.scanLine, { transform: [{ translateY }] }]} />
                                <View style={styles.reticleCorners} />
                                <View style={styles.simulationBadge}>
                                    <ActivityIndicator size="small" color="#00f3ff" />
                                    <Text style={styles.simText}>ANALYZING TARGET...</Text>
                                </View>
                            </>
                        )}
                    </View>

                    {/* Right: Tactical Sidebar */}
                    <View style={styles.controlsSidebar}>
                        <View style={styles.sidebarGroup}>
                            <TouchableOpacity onPress={() => handleZoom(0.1)} style={styles.sidebarBtn}>
                                <ZoomIn size={24} color="#00f3ff" />
                            </TouchableOpacity>
                            <Text style={styles.zoomText}>{(zoom * 10).toFixed(0)}X</Text>
                            <TouchableOpacity onPress={() => handleZoom(-0.1)} style={styles.sidebarBtn}>
                                <ZoomOut size={24} color="#00f3ff" />
                            </TouchableOpacity>
                        </View>

                        <TouchableOpacity
                            style={[styles.sidebarBtn, torch && styles.btnActive]}
                            onPress={() => { setTorch(t => !t); Haptics.selectionAsync(); }}
                        >
                            <Flashlight size={24} color={torch ? "#000" : "#00f3ff"} />
                        </TouchableOpacity>
                    </View>
                </View>

                {/* 3. Bottom HUD Footer */}
                <View style={styles.bottomHud}>
                    <View style={styles.footerData}>
                        <Zap size={16} color="#00f3ff" />
                        <Text style={styles.footerText}>
                            {isAutoScan && frameCounter > 0 ? `FRAMES: ${frameCounter}` : "PWR: 100%"}
                        </Text>
                    </View>

                    {!isAutoScan ? (
                        <TouchableOpacity style={styles.mainTrigger} onPress={() => processFrame(true)} disabled={scanning}>
                            <View style={styles.triggerInner}>
                                <Scan size={32} color={scanning ? "#555" : "#00f3ff"} />
                            </View>
                        </TouchableOpacity>
                    ) : (
                        <View style={styles.autoPilotDisplay}>
                            <Text style={styles.autoPilotText}>AUTO-PILOT ACTIVE</Text>
                        </View>
                    )}

                    <View style={styles.switchWrapper}>
                        <Text style={styles.switchLabel}>AUTO</Text>
                        <Switch
                            trackColor={{ false: "#1a1a1a", true: "rgba(0, 243, 255, 0.3)" }}
                            thumbColor={isAutoScan ? "#00f3ff" : "#555"}
                            onValueChange={() => setIsAutoScan(p => !p)}
                            value={isAutoScan}
                        />
                    </View>
                </View>
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#000' },
    message: { textAlign: 'center', paddingBottom: 10, color: '#00f3ff', fontFamily: 'monospace' },
    button: { backgroundColor: '#00f3ff', padding: 12, borderRadius: 2, alignSelf: 'center' },
    text: { color: '#000', fontWeight: 'bold' },
    overlay: { ...StyleSheet.absoluteFillObject, justifyContent: 'space-between' },

    // --- Bounding Box ---
    bbox: {
        position: 'absolute',
        borderWidth: 2,
        borderRadius: 4,
        zIndex: 20, // Above overlay elements
    },
    bboxLabel: {
        position: 'absolute',
        top: -20,
        left: 0,
        paddingHorizontal: 6,
        paddingVertical: 2,
        borderRadius: 2,
    },
    bboxText: {
        color: '#000',
        fontSize: 10,
        fontWeight: 'bold',
        textTransform: 'uppercase',
    },
    cornerTL: { position: 'absolute', top: -1, left: -1, width: 10, height: 10, borderTopWidth: 4, borderLeftWidth: 4, borderColor: 'rgba(255,255,255,0.7)' },
    cornerTR: { position: 'absolute', top: -1, right: -1, width: 10, height: 10, borderTopWidth: 4, borderRightWidth: 4, borderColor: 'rgba(255,255,255,0.7)' },
    cornerBL: { position: 'absolute', bottom: -1, left: -1, width: 10, height: 10, borderBottomWidth: 4, borderLeftWidth: 4, borderColor: 'rgba(255,255,255,0.7)' },
    cornerBR: { position: 'absolute', bottom: -1, right: -1, width: 10, height: 10, borderBottomWidth: 4, borderRightWidth: 4, borderColor: 'rgba(255,255,255,0.7)' },


    // --- TOP HUD ---
    topHud: {
        flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
        paddingTop: Platform.OS === 'android' ? 40 : 10,
        paddingHorizontal: 20,
        paddingBottom: 20,
        backgroundColor: 'rgba(0,0,0,0.0)', // Transparent
    },
    backBtn: {
        width: 40, height: 40, alignItems: 'center', justifyContent: 'center',
        borderWidth: 1, borderColor: 'rgba(0,243,255,0.3)', borderRadius: 4,
        backgroundColor: 'rgba(0,0,0,0.5)',
    },
    statusDisplay: {
        flexDirection: 'row', alignItems: 'center', gap: 8,
        borderWidth: 1, borderColor: '#00f3ff', borderRadius: 4,
        paddingHorizontal: 12, paddingVertical: 6,
        backgroundColor: 'rgba(0, 243, 255, 0.1)',
    },
    statusDot: { width: 8, height: 8, borderRadius: 1 },
    statusText: { color: '#00f3ff', fontSize: 12, fontFamily: 'monospace', letterSpacing: 2 },
    topRightDecoration: { width: 40, height: 2, backgroundColor: '#00f3ff' },

    // --- MAIN AREA ---
    mainArea: { flex: 1, flexDirection: 'row' },

    // Result Zone (overlay)
    resultZone: {
        position: 'absolute', top: 20, left: 20, right: 80, // Leave room for sidebar
        zIndex: 10,
    },
    resultCard: {
        backgroundColor: 'rgba(5, 10, 20, 0.9)',
        borderWidth: 1, borderColor: '#00f3ff', borderRadius: 2,
        padding: 15,
        shadowColor: '#00f3ff', shadowOpacity: 0.2, shadowRadius: 20,
    },
    cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
    emoji: { fontSize: 32, marginRight: 15 },
    animalTitle: { color: '#00f3ff', fontSize: 20, fontWeight: '900', fontFamily: 'monospace', letterSpacing: 1 },
    confidenceText: { color: '#5eead4', fontSize: 10, fontFamily: 'monospace' },
    divider: { height: 1, backgroundColor: 'rgba(0,243,255,0.3)', marginVertical: 8 },
    statsGrid: { flexDirection: 'row', gap: 20, marginBottom: 8 },
    statItem: { alignItems: 'center', flex: 1, },
    statLabel: { color: '#5eead4', fontSize: 9, marginBottom: 2, textTransform: 'uppercase' },
    statValue: { color: '#fff', fontSize: 12, fontFamily: 'monospace' },
    factText: { color: '#a5f3fc', fontSize: 12, lineHeight: 16, fontStyle: 'italic' },

    // Center Scanning Reticle
    reticleZone: { flex: 1, justifyContent: 'center', alignItems: 'center', position: 'relative' },
    reticleCorners: {
        width: 250, height: 250,
        borderWidth: 2, borderColor: 'rgba(0,243,255,0.3)', borderStyle: 'dashed',
        position: 'absolute'
    },
    scanLine: { width: '80%', height: 2, backgroundColor: '#00f3ff', opacity: 0.8, position: 'absolute', top: 0 },
    simulationBadge: {
        position: 'absolute', top: '65%',
        flexDirection: 'row', alignItems: 'center', gap: 8,
        backgroundColor: 'rgba(0,0,0,0.8)', padding: 8, borderRadius: 4,
        borderWidth: 1, borderColor: '#00f3ff',
    },
    simText: { color: '#00f3ff', fontSize: 10, fontFamily: 'monospace', letterSpacing: 1 },

    // Right Sidebar
    controlsSidebar: {
        width: 60, height: '100%',
        alignItems: 'center', justifyContent: 'center', gap: 30,
        backgroundColor: 'rgba(0,0,0,0.3)',
        borderLeftWidth: 1, borderLeftColor: 'rgba(0,243,255,0.2)',
    },
    sidebarGroup: { alignItems: 'center', gap: 10 },
    sidebarBtn: {
        width: 44, height: 44, borderRadius: 22,
        alignItems: 'center', justifyContent: 'center',
        borderWidth: 1, borderColor: '#00f3ff',
        backgroundColor: 'rgba(0,20,30,0.8)',
    },
    btnActive: { backgroundColor: '#00f3ff' },
    zoomText: { color: '#fff', fontSize: 12, fontFamily: 'monospace' },

    // --- BOTTOM HUD ---
    bottomHud: {
        height: 100, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
        paddingHorizontal: 30,
        backgroundColor: 'rgba(0,0,0,0.8)',
        borderTopWidth: 1, borderTopColor: '#00f3ff',
    },
    footerData: { alignItems: 'center', gap: 4 },
    footerText: { color: '#00f3ff', fontSize: 10, fontFamily: 'monospace' },

    // Main Trigger
    mainTrigger: {
        width: 70, height: 70, borderRadius: 35,
        borderWidth: 2, borderColor: '#00f3ff',
        alignItems: 'center', justifyContent: 'center',
        backgroundColor: 'rgba(0,243,255,0.1)',
        shadowColor: '#00f3ff', shadowOpacity: 0.6, shadowRadius: 15, elevation: 10,
    },
    triggerInner: {
        width: 50, height: 50, borderRadius: 25,
        backgroundColor: 'rgba(0,0,0,0.8)',
        alignItems: 'center', justifyContent: 'center',
    },
    autoPilotDisplay: {
        borderWidth: 1, borderColor: '#00f3ff', padding: 10,
        backgroundColor: 'rgba(0, 243, 255, 0.2)',
    },
    autoPilotText: { color: '#00f3ff', fontWeight: 'bold', letterSpacing: 2 },

    switchWrapper: { alignItems: 'center', gap: 4 },
    switchLabel: { color: '#5eead4', fontSize: 10, letterSpacing: 1 },

    // Cinematic Elements
    corner: { position: 'absolute', width: 40, height: 40, borderColor: 'rgba(0, 243, 255, 0.5)', borderWidth: 4 },
    tl: { top: 20, left: 20, borderRightWidth: 0, borderBottomWidth: 0 },
    tr: { top: 20, right: 20, borderLeftWidth: 0, borderBottomWidth: 0 },
    bl: { bottom: 20, left: 20, borderRightWidth: 0, borderTopWidth: 0 },
    br: { bottom: 20, right: 20, borderLeftWidth: 0, borderTopWidth: 0 },

    dataStreamContainer: { position: 'absolute', top: 180, left: 20, width: 200 },
    logText: { color: '#00f3ff', fontSize: 10, fontFamily: 'monospace', marginBottom: 2, textShadowColor: '#00f3ff', textShadowRadius: 2 },
});
