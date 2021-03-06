# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

from emokit.emotiv import Emotiv
import platform
if platform.system() == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459)
import gevent
import threading
import logging
from time import sleep
from numpy import sin, arange, pi, sqrt
from scipy.signal import lfilter, firwin, periodogram
from pylab import figure, plot, grid, show
global signal
signal = None

class SSVEPAnalizer():
    def __init__(self):
        self.signal = signal
        pass
    def analize(self,signals,sensors,bufferlength, frecs):
            #logging.debug("Analize")
            nSamples = bufferlength
            sampleRate = 128. #this is the epoc rate
            t = arange(nSamples) / sampleRate
            cutoff_hz = 60
            nyq_rate = sampleRate / 2.
            numtaps = 29
            fir_coeff = firwin(numtaps, cutoff_hz/nyq_rate)
            results = {}
            #sensors = 'AF3 F7 F3 FC5 T7 P7 O1 O2 P8 T8 FC6 F4 F8 AF4'.split(' ')      
            for name in sensors:
                #print signals[name]
                filtered_signal = lfilter(fir_coeff, 1.0, signals[name])
                warmup = numtaps - 1
                #print filtered_signal
                # The phase delay of the filtered signal
                delay = (warmup / 2) / sampleRate
                #print(len(signals[name]))
                #print "\n"
               
                fres, espect = periodogram(filtered_signal, sampleRate)

                #print max frec 
                maxFrec = True
                if maxFrec:
                    mespect = max(espect)
                    i=0
                    while espect[i]!= mespect: i+=1
                    print "max frec=",fres[i]

                frecs.sort()
                results[name] = []
                for x in frecs:
                    flow = x-1
                    fhight =  x + 1
                    i = 0
                    while fres[i]< flow: i+=1
                    debugflist =  filter(lambda x: x>=flow  and x <= fhight,fres)
                    debugAlist =  espect[i:i+len(debugflist)]
                    #print debugflist,"\n",debugAlist                
                    frecAvg =  sum(debugAlist)/len(debugAlist)
                    results[name].append(frecAvg)
                    pass

                if False:
                    figure(1)
                    plot(t,signals[name])
                    plot(t-delay,filtered_signal,'r')
                    plot(t[warmup:]-delay, filtered_signal[warmup:], 'g', linewidth=4)
                    grid(True)

                    figure(2)
                    plot(fres, espect)


                    show()
                    pass

                pass
            
            results["avg"] = []
            for i in range(len(frecs)):
                fi=map(lambda n: results[n][0],sensors)
                results["avg"].append(sum(fi)/len(fi))
            #print results
            return results          
            pass

    def analizeProccess(self):

        headset = Emotiv(display_output = False)
        gevent.spawn(headset.setup)
        gevent.sleep(0)
        packets = {};
        bufferLenght = 128*3
        sensors = "O1 O2".split(' ')
        print "analize"
        for name in sensors:
            packets[name] = []
            pass
        while True:
                p = headset.dequeue()
                if p != None:
                    for name in sensors:
                        packets[name].append(p.sensors[name]['value'])
                        pass
                   
                    if len(packets[sensors[0]]) >= bufferLenght:
                        self.signal = self.analize(packets,sensors,bufferLenght,[8,12])
                        #print self.signal
                        for name in sensors:
                            packets[name] = packets[name][5:]
                            pass
                        pass
                gevent.sleep(0)
        pass


if __name__ == "__main__":
    try:
        analizer = SSVEPAnalizer()
        gevent.spawn(analizer.analizeProccess)
        gevent.sleep(0)
        while True:
            print analizer.signal 
            gevent.sleep(0)
            pass
    except KeyboardInterrupt:
        #headset.close()
        pass
    finally:
        #headset.close()
        pass
    print "Exit!!!"
