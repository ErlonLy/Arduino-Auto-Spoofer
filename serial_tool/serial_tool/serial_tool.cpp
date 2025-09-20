#include <windows.h>
#include <setupapi.h>
#include <initguid.h>
#include <devguid.h>
#include <iostream>
#include <string>
#include <vector>
#include <regex>

// Linkagem necessária
#pragma comment(lib, "setupapi.lib")

// Estrutura para armazenar informações da porta
struct SerialPortInfo {
    std::string port;
    std::string description;
    std::string hardwareId;
};

// Função para listar todas as portas seriais
std::vector<SerialPortInfo> list_serial_ports() {
    std::vector<SerialPortInfo> ports;

    HDEVINFO deviceInfoSet = SetupDiGetClassDevs(
        &GUID_DEVCLASS_PORTS, nullptr, nullptr, DIGCF_PRESENT);

    if (deviceInfoSet == INVALID_HANDLE_VALUE) {
        return ports;
    }

    SP_DEVINFO_DATA deviceInfoData;
    deviceInfoData.cbSize = sizeof(SP_DEVINFO_DATA);

    DWORD index = 0;
    while (SetupDiEnumDeviceInfo(deviceInfoSet, index, &deviceInfoData)) {
        index++;

        char deviceInstanceId[256];
        SetupDiGetDeviceInstanceIdA(deviceInfoSet, &deviceInfoData,
            deviceInstanceId, sizeof(deviceInstanceId), nullptr);

        HKEY hDeviceRegistryKey = SetupDiOpenDevRegKey(
            deviceInfoSet, &deviceInfoData, DICS_FLAG_GLOBAL, 0,
            DIREG_DEV, KEY_READ);

        if (hDeviceRegistryKey == INVALID_HANDLE_VALUE) continue;

        char portName[256];
        DWORD portNameSize = sizeof(portName);
        DWORD type = 0;

        if (RegQueryValueExA(hDeviceRegistryKey, "PortName", nullptr, &type,
            (LPBYTE)portName, &portNameSize) == ERROR_SUCCESS) {
            if (std::regex_match(portName, std::regex("COM[0-9]+"))) {
                // Descrição do dispositivo
                char friendlyName[256];
                DWORD friendlyNameSize = sizeof(friendlyName);
                if (SetupDiGetDeviceRegistryPropertyA(
                    deviceInfoSet, &deviceInfoData, SPDRP_FRIENDLYNAME,
                    nullptr, (PBYTE)friendlyName, friendlyNameSize, nullptr)) {
                    ports.push_back({ portName, friendlyName, deviceInstanceId });
                }
                else {
                    ports.push_back({ portName, "Dispositivo Serial", deviceInstanceId });
                }
            }
        }
        RegCloseKey(hDeviceRegistryKey);
    }

    SetupDiDestroyDeviceInfoList(deviceInfoSet);
    return ports;
}

// Funções simuladas (adaptar depois)
void verify_port(const std::string& port) {
    std::cout << "PASSIVO " << port << std::endl;
}
void get_status(const std::string& port) {
    std::cout << "STATUS OK em " << port << std::endl;
}
void spoof_device(const std::string& port, const std::string& vid, const std::string& pid) {
    std::cout << "SPOOF " << port << " VID=" << vid << " PID=" << pid << std::endl;
}

// ---------------- MAIN ----------------
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Uso: serial_tool.exe [list|verify|status|spoof] ..." << std::endl;
        return 1;
    }

    std::string command = argv[1];

    if (command == "list") {
        auto ports = list_serial_ports();
        for (auto& p : ports) {
            std::cout << p.port << " - " << p.description << std::endl;
        }
        return 0;
    }

    if (argc < 3) {
        std::cerr << "Uso inválido. Porta necessária." << std::endl;
        return 1;
    }

    std::string port = argv[2];

    if (command == "verify") {
        verify_port(port);
    }
    else if (command == "status") {
        get_status(port);
    }
    else if (command == "spoof") {
        if (argc < 5) {
            std::cerr << "Uso: serial_tool.exe spoof <porta> <vid> <pid>" << std::endl;
            return 1;
        }
        std::string vid = argv[3];
        std::string pid = argv[4];
        spoof_device(port, vid, pid);
    }
    else {
        std::cerr << "Comando inválido: " << command << std::endl;
        return 1;
    }

    return 0;
}
