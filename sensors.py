import smbus  # import SMBus module of I2C
import time


class sensors:
    def __init__(self):
        # some MPU6050 Registers and their Address
        self.PWR_MGMT_1 = 0x6B
        self.SMPLRT_DIV = 0x19
        self.CONFIG = 0x1A
        self.GYRO_CONFIG = 0x1B
        self.INT_ENABLE = 0x38
        self.ACCEL_XOUT_H = 0x3B
        self.ACCEL_YOUT_H = 0x3D
        self.ACCEL_ZOUT_H = 0x3F
        self.GYRO_XOUT_H = 0x43
        self.GYRO_YOUT_H = 0x45
        self.GYRO_ZOUT_H = 0x47
        self.Device_Address_MPU = 0x68  # MPU6050 device address

        # some HMC5883L Registers and their Address
        self.Register_A = 0  # Address of Configuration register A
        self.Register_B = 0x01  # Address of configuration register B
        self.Register_mode = 0x02  # Address of mode register
        self.X_axis_H = 0x03  # Address of X-axis MSB data register
        self.Z_axis_H = 0x05  # Address of Z-axis MSB data register
        self.Y_axis_H = 0x07  # Address of Y-axis MSB data register
        self.Device_Address_HMC = 0x1e  # HMC5883L magnetometer device address

        self.bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards

        self.MPU_Init()
        self.Magnetometer_Init()  # initialize HMC5883L magnetometer
        self.Baro_Init()

    def MPU_Init(self):
        # write to sample rate register
        self.bus.write_byte_data(self.Device_Address_MPU, self.SMPLRT_DIV, 7)

        # Write to power management register
        self.bus.write_byte_data(self.Device_Address_MPU, self.PWR_MGMT_1, 1)

        # Write to Configuration register
        self.bus.write_byte_data(self.Device_Address_MPU, self.CONFIG, 0)

        # Write to Gyro configuration register
        self.bus.write_byte_data(self.Device_Address_MPU, self.GYRO_CONFIG, 24)

        # Write to interrupt enable register
        self.bus.write_byte_data(self.Device_Address_MPU, self.INT_ENABLE, 1)
        # Write registers to enable access to magnetometer
        self.bus.write_byte_data(self.Device_Address_MPU, 0x37, 0x02)
        self.bus.write_byte_data(self.Device_Address_MPU, 0x6a, 0x00)
        self.bus.write_byte_data(self.Device_Address_MPU, 0x6b, 0x00)

    def read_raw_data_MPU(self, addr):
        # Accelero and Gyro value are 16-bit
        high = self.bus.read_byte_data(self.Device_Address_MPU, addr)
        low  = self.bus.read_byte_data(self.Device_Address_MPU, addr + 1)

        # concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from mpu6050
        if (value > 32768):
            value = value - 65536
        return value

    def Magnetometer_Init(self):
        # write to Configuration Register A
        self.bus.write_byte_data(self.Device_Address_HMC, self.Register_A, 0x70)

        # Write to Configuration Register B for gain
        self.bus.write_byte_data(self.Device_Address_HMC, self.Register_B, 0xa0)

        # Write to mode Register for selecting mode
        self.bus.write_byte_data(self.Device_Address_HMC, self.Register_mode, 0)

    def read_raw_data_HMC(self, addr):
        # Read raw 16-bit value
        high = self.bus.read_byte_data(self.Device_Address_HMC, addr)
        low = self.bus.read_byte_data(self.Device_Address_HMC, addr + 1)

        # concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from module
        if (value > 32768):
            value = value - 65536
        return value

    def Baro_Init(self):
        # MS5611_01BXXX address, 0x77(119)
        # 0x1E(30) Reset command
        self.bus.write_byte(0x77, 0x1E)
        time.sleep(0.5)
        # Read 12 bytes of calibration data
        # Read pressure sensitivity
        data = self.bus.read_i2c_block_data(0x77, 0xA2, 2)
        self.C1 = data[0] * 256 + data[1]
        # Read pressure offset
        data = self.bus.read_i2c_block_data(0x77, 0xA4, 2)
        self.C2 = data[0] * 256 + data[1]
        # Read temperature coefficient of pressure sensitivity
        data = self.bus.read_i2c_block_data(0x77, 0xA6, 2)
        self.C3 = data[0] * 256 + data[1]
        # Read temperature coefficient of pressure offset
        data = self.bus.read_i2c_block_data(0x77, 0xA8, 2)
        self.C4 = data[0] * 256 + data[1]
        # Read reference temperature
        data = self.bus.read_i2c_block_data(0x77, 0xAA, 2)
        self.C5 = data[0] * 256 + data[1]
        # Read temperature coefficient of the temperature
        data = self.bus.read_i2c_block_data(0x77, 0xAC, 2)
        self.C6 = data[0] * 256 + data[1]

    def read_mag_raw(self):
        # Read Magnetometer raw value
        x = self.read_raw_data_HMC(self.X_axis_H)
        z = self.read_raw_data_HMC(self.Z_axis_H)
        y = self.read_raw_data_HMC(self.Y_axis_H)
        return {'x': x, 'y': y, 'z': z, 'unit': 'a.u.'}

    def read_mag(self):
        #convert using default gain
        data = self.read_mag_raw()
        data['x'] = data['x'] / 390.0
        data['y'] = data['y'] / 390.0
        data['z'] = data['z'] / 390.0
        data['unit'] = 'Gauss'
        return data

    def read_acc_raw(self):
        # Read Accelerometer raw value
        x = self.read_raw_data_MPU(self.ACCEL_XOUT_H)
        y = self.read_raw_data_MPU(self.ACCEL_YOUT_H)
        z = self.read_raw_data_MPU(self.ACCEL_ZOUT_H)
        return {'x': x, 'y': y, 'z': z, 'unit': 'a.u.'}

    def read_acc(self):
        #convert using default gain
        data = self.read_acc_raw()
        data['x'] = data['x'] / 16384.0
        data['y'] = data['y'] / 16384.0
        data['z'] = data['z'] / 16384.0
        data['unit'] = 'G'
        return data

    def read_gyro_raw(self):
        # Read Accelerometer raw value
        x = self.read_raw_data_MPU(self.GYRO_XOUT_H)
        y = self.read_raw_data_MPU(self.GYRO_YOUT_H)
        z = self.read_raw_data_MPU(self.GYRO_ZOUT_H)
        return {'x': x, 'y': y, 'z': z, 'unit': 'a.u.'}

    def read_gyro(self):
        # convert using default gain
        data = self.read_gyro_raw()
        data['x'] = data['x'] / 131.0
        data['y'] = data['y'] / 131.0
        data['z'] = data['z'] / 131.0
        data['unit'] = 'deg/s'
        return data

    def read_press_temp(self):
        # MS5611_01BXXX address, 0x77(118)
        # 0x40(64) Pressure conversion(OSR = 256) command
        self.bus.write_byte(0x77, 0x40)
        time.sleep(0.015)
        # Read digital pressure value
        # Read data back from 0x00(0), 3 bytes
        # D1 MSB2, D1 MSB1, D1 LSB
        value = self.bus.read_i2c_block_data(0x77, 0x00, 3)
        D1 = value[0] * 65536 + value[1] * 256 + value[2]
        # MS5611_01BXXX address, 0x76(118)
        # 0x50(64) Temperature conversion(OSR = 256) command
        self.bus.write_byte(0x77, 0x50)
        time.sleep(0.015)
        # Read digital temperature value
        # Read data back from 0x00(0), 3 bytes
        # D2 MSB2, D2 MSB1, D2 LSB
        value = self.bus.read_i2c_block_data(0x77, 0x00, 3)
        D2 = value[0] * 65536 + value[1] * 256 + value[2]
        dT = D2 - self.C5 * 256
        TEMP = 2000 + dT * self.C6 / 8388608
        OFF = self.C2 * 65536 + (self.C4 * dT) / 128
        SENS = self.C1 * 32768 + (self.C3 * dT) / 256
        T2 = 0
        OFF2 = 0
        SENS2 = 0
        if TEMP >= 2000:
            T2 = 0
            OFF2 = 0
            SENS2 = 0
        elif TEMP < 2000:
            T2 = (dT * dT) / 2147483648
            OFF2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 2
            SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 4
            if TEMP < -1500:
                OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
                SENS2 = SENS2 + 11 * ((TEMP + 1500) * (TEMP + 1500)) / 2
        TEMP = TEMP - T2
        OFF = OFF - OFF2
        SENS = SENS - SENS2
        pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
        cTemp = TEMP / 100.0

        return {'p': pressure, 't': cTemp, 'unit_p': 'mbar', 'unit_t': 'deg C'}


for i in range(1, 1201):
    
    time.sleep(0.5)
