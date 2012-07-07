#!/usr/bin/python

import pickle

TRAFFIC_FILE = 'network_traffic.pkl'

def get_network_io():
    try:
        proc = open('/proc/net/dev', 'r')
        lines = proc.readlines()
        proc.close()

    except IOError, e:
        return False

    columnLine = lines[1]
    _, receiveCols , transmitCols = columnLine.split('|')
    receiveCols = map(lambda a:'recv_' + a, receiveCols.split())
    transmitCols = map(lambda a:'trans_' + a, transmitCols.split())

    cols = receiveCols + transmitCols

    faces = {}
    for line in lines[2:]:
        if line.find(':') < 0: continue
        face, data = line.split(':')
        face_data = dict(zip(cols, data.split()))
        faces[face] = face_data

    interfaces = {}

    # Reading old data from the file to compare
    try:
        traffic_file = open(TRAFFIC_FILE, 'rb')
        network_traffic_store = pickle.load(traffic_file)
        traffic_file.close()
    except:
        network_traffic_store = {}

    # Now loop through each interface
    for face in faces:
        key = face.strip()

        # We need to work out the traffic since the last check so first time we store the current value
        # then the next time we can calculate the difference
        try:
            if key in network_traffic_store:
                interfaces[key] = {}
                interfaces[key]['recv_bytes'] = long(faces[face]['recv_bytes']) - long(network_traffic_store[key]['recv_bytes'])
                interfaces[key]['trans_bytes'] = long(faces[face]['trans_bytes']) - long(network_traffic_store[key]['trans_bytes'])

                if interfaces[key]['recv_bytes'] < 0:
                    interfaces[key]['recv_bytes'] = long(faces[face]['recv_bytes'])

                if interfaces[key]['trans_bytes'] < 0:
                    interfaces[key]['trans_bytes'] = long(faces[face]['trans_bytes'])

                interfaces[key]['recv_bytes'] = str(interfaces[key]['recv_bytes'])
                interfaces[key]['trans_bytes'] = str(interfaces[key]['trans_bytes'])

                # And update the stored value to subtract next time round
                network_traffic_store[key]['recv_bytes'] = faces[face]['recv_bytes']
                network_traffic_store[key]['trans_bytes'] = faces[face]['trans_bytes']
                
            else:
                network_traffic_store[key] = {}
                network_traffic_store[key]['recv_bytes'] = faces[face]['recv_bytes']
                network_traffic_store[key]['trans_bytes'] = faces[face]['trans_bytes']

            # Writing current data back to the file
            network_output = open(TRAFFIC_FILE, 'wb')
            pickle.dump(network_traffic_store, network_output)
            network_output.close()

        except KeyError, ex:
            pass

        except ValueError, ex:
            pass

    return interfaces

if __name__ == '__main__':
    print get_network_io()
