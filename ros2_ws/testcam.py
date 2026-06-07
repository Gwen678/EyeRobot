import depthai as dai
import time

# Pipeline de base
pipeline = dai.Pipeline()
imu = pipeline.create(dai.node.IMU)
xlinkOut = pipeline.create(dai.node.XLinkOut)
xlinkOut.setStreamName("imu")

# Activation large pour voir ce qui sort
imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, 50)
imu.enableIMUSensor(dai.IMUSensor.GYROSCOPE_RAW, 50)
imu.out.link(xlinkOut.input)

print("--- Inspection du flux IMU démarrée ---")

with dai.Device(pipeline) as device:
    imuQueue = device.getOutputQueue(name="imu", maxSize=10, blocking=False)
    
    try:
        while True:
            if imuQueue.has():
                imuData = imuQueue.get()
                packets = imuData.packets
                
                print(f"\n--- Nouveau paquet (Nombre de capteurs: {len(packets)}) ---")
                
                for i, packet in enumerate(packets):
                    # Inspection par réflexion : on liste tout ce que le paquet contient
                    attributes = [attr for attr in dir(packet) if not attr.startswith('__')]
                    print(f"Capteur {i} possède les attributs : {attributes}")
                    
                    # Si c'est l'accéléromètre
                    if hasattr(packet, 'acceleroMeter'):
                        data = packet.acceleroMeter
                        print(f"-> Accel [X:{data.x:.2f}, Y:{data.y:.2f}, Z:{data.z:.2f}]")
                    
                    # Si c'est le gyroscope
                    if hasattr(packet, 'gyroscope'):
                        data = packet.gyroscope
                        print(f"-> Gyro [X:{data.x:.2f}, Y:{data.y:.2f}, Z:{data.z:.2f}]")
            
            time.sleep(1) # Ralenti pour pouvoir lire le terminal
            
    except KeyboardInterrupt:
        print("\nArrêt.")
