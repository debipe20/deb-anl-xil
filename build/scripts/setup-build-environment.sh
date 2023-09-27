

#Request the user-name, user-group, and architecture
read -p "Username: " username
read -p "User Group: " usergroup
read -p "Architecture - x86 or arm: " arch
read -p "Name of network adapter to be used by deb-anl-xil: " deb_anl_xil_network_adapter
read -p "Copy sample configuration file to /nojournal/bin? (y or n): " copy_sample 

echo "Adding DEB_ANL_XIL_ROOT to ~/.bashrc"
echo "export DEB_ANL_XIL_ROOT=$(pwd)/../../.." >> ~/.bashrc

echo "Adding DEB_ANL_XIL_NETWORK_ADAPTER to ~/.bashrc"
echo "export DEB_ANL_XIL_NETWORK_ADAPTER=$deb_anl_xil_network_adapter" >> ~/.bashrc

echo "Adding PROCESSOR to ~/.bashrc"
echo "export PROCESSOR=$arch" >> ~/.bashrc

echo "Adding environment variable required for SNMP sessions to ~/.bashrc"
echo "export MIBS=ALL" >> ~/.bashrc

echo "Creating required directories in the root folder."
sudo rm -r /nojournal/
sudo rm -r /usr/local/lib/deb-anl-xil
sudo mkdir -p /nojournal/bin/log
sudo mkdir /usr/local/lib/deb-anl-xil
sleep 1s

if [ "$copy_sample" = "y" ]; then
echo "Copy the configuration files of the intersection speedway-mountain to /nojournal/bin/"
sudo cp -r ../../config/speedway-sample/simulation/speedway-mountain/nojournal/bin /nojournal
sudo cp ../../config/anl-master-config.json /nojournal/bin
sleep 1s
echo "Change the owner and group of the configuration files and provide necessary permissions (chmod 777)"
sudo chown -R $username:$usergroup /nojournal
sudo chmod -R 777 /nojournal
sleep 1s
fi

echo "Add the shared libraries we need to run"

if [ "$arch" = "x86" ]; then
sudo cp ../../3rdparty/net-snmp/lib/x86/libnetsnmp.so.35.0.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../3rdparty/glpk/lib/x86/libglpk.so.35.1.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../lib/x86/libmmitss-common.so /usr/local/lib/deb-anl-xil/
sudo cp ../../3rdparty/mapengine/lib/x86/liblocAware.so.1.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../3rdparty/asn1j2735/lib/x86/libasn.so.1.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../3rdparty/asn1j2735/lib/x86/libdsrc.so.1.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../lib/deb-anl-xil.conf /etc/ld.so.conf.d/

echo "Create the symbolic links for the copied libraries."

sudo ln -s /usr/local/lib/deb-anl-xil/libnetsnmp.so.35.0.0 /usr/local/lib/deb-anl-xil/libnetsnmp.so.35
sudo ln -s /usr/local/lib/deb-anl-xil/libglpk.so.35.1.0 /usr/local/lib/deb-anl-xil/libglpk.so.35
sudo ln -s /usr/local/lib/deb-anl-xil/liblocAware.so.1.0 /usr/local/lib/deb-anl-xil/liblocAware.so
sudo ln -s /usr/local/lib/deb-anl-xil/libasn.so.1.0 /usr/local/lib/deb-anl-xil/libasn.so
sudo ln -s /usr/local/lib/deb-anl-xil/libdsrc.so.1.0 /usr/local/lib/deb-anl-xil/libdsrc.so
fi

if [ "$arch" = "arm" ]; then
sudo cp ../../3rdparty/net-snmp/lib/arm/libnetsnmp.so.35.0.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../3rdparty/glpk/lib/arm/libglpk.so.40.3.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../lib/arm/libmmitss-common.so /usr/local/lib/deb-anl-xil/
sudo cp ../../3rdparty/mapengine/lib/arm/liblocAware.so.1.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../3rdparty/asn1j2735/lib/arm/libasn.so.1.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../3rdparty/asn1j2735/lib/arm/libdsrc.so.1.0 /usr/local/lib/deb-anl-xil/
sudo cp ../../lib/deb-anl-xil.conf /etc/ld.so.conf.d/
sudo cp ../../3rdparty/openssl/* /usr/local/lib

echo "Create the symbolic links for the copied libraries."

sudo ln -s /usr/local/lib/deb-anl-xil/libnetsnmp.so.35.0.0 /usr/local/lib/deb-anl-xil/libnetsnmp.so.35
sudo ln -s /usr/local/lib/deb-anl-xil/libglpk.so.40.3.0 /usr/local/lib/deb-anl-xil/libglpk.so.40
sudo ln -s /usr/local/lib/deb-anl-xil/liblocAware.so.1.0 /usr/local/lib/deb-anl-xil/liblocAware.so
sudo ln -s /usr/local/lib/deb-anl-xil/libasn.so.1.0 /usr/local/lib/deb-anl-xil/libasn.so
sudo ln -s /usr/local/lib/deb-anl-xil/libdsrc.so.1.0 /usr/local/lib/deb-anl-xil/libdsrc.so
fi

sleep 1s

sudo ldconfig

sleep 2s
echo "Added required environment variables in ~/.bashrc file."
echo "To allow for changes to take effect, either close this terminal or execute the command: source ~/.bashrc"
pkill -9 sleep #End
