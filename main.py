import SetupParser
import MainProcess

if __name__ == '__main__':
    print("Initializing...")
    configuration = SetupParser.read_setup()
    main_process = MainProcess.MainProcess(configuration)
    main_process.run()
