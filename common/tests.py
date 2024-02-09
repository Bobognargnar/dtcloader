from django.test import TestCase
from common.models import File
from common.utils import DataFlowParserFactory,BaseDataFlowParser,D0010Parser
from random import randint
import uuid
import os
import shutil
from django.db import IntegrityError

class FileUploadTest(TestCase):
    def test_upload(self):
        file = ".\DTC5259515123502080915D0010.uff"
        file_instance = File(filename = "DTC5259515123502080915D0010.uff" )
        file_instance.file.save(os.path.basename(file), open(file, 'rb'))
        pass

    def test_upload_missing(self):
        with self.assertRaises(FileNotFoundError) as context:
            file = ".\\fantasy.uff"
            file_instance = File(filename = "DTC5259515123502080915D0010.uff" )
            file_instance.file.save(os.path.basename(file), open(file, 'rb'))
        pass

    def test_upload_invalid_extension(self):

        file = ".\demo.bad"
        if os.path.exists(file): os.remove(file)

        shutil.copy2(".\DTC5259515123502080915D0010.uff", file)

        with self.assertRaises(IntegrityError) as context:
            file_instance = File(filename = "DTC5259515123502080915D0010.uff" )
            file_instance.file.save(os.path.basename(file), open(file, 'rb'))
            
        if os.path.exists(file): os.remove(file)

    def test_upload_invalid_flow(self):

        file = ".\demo.uff"
        if os.path.exists(file): os.remove(file)

        shutil.copy2(".\DTC5259515123502080915D0010.uff", file)

        with open(file, 'r+') as f:
            content = f.read()
            modified_content = content.replace('D0010002', 'D0020002')
            f.seek(0)
            f.write(modified_content)
            f.truncate()

        with self.assertRaises(NotImplementedError) as context:
            file_instance = File(filename = "DTC5259515123502080915D0010.uff" )
            file_instance.file.save(os.path.basename(file), open(file, 'rb'))
            
        #if os.path.exists(file): os.remove(file)

class D0010Test(TestCase):

    def test_parse_D0010(self):
        # Receive D0010 flow file, parse content 
        file_content = DataFlowFactory().get_data_flow("D0010")
        
        flow_parser = D0010Parser()
        
        data = flow_parser.process(file_content)

        self.assertEqual(len(data),13)
        pass

    def test_parse_D0010_no_readings(self):
        # Receive D0010 flow file with not readings
        tmp_file_content = DataFlowFactory().get_data_flow("D0010")
        file_content = []
        for row in tmp_file_content:
            if row[0:3]!="030":
                file_content.append(row)
        
        flow_parser = DataFlowParserFactory().get_parser(file_content)        
        flow_parser = D0010Parser()
        data = flow_parser.process(file_content)
        
        self.assertListEqual(data,[])
        pass

    def test_parse_D0010_bad_readings(self):
        # Receive D0010 flow file with bad or malformed readings
        tmp_file_content = DataFlowFactory().get_data_flow("D0010")
        file_content = []

        bad_reading = []
        for row in tmp_file_content:
            if row[0:3]=="030" and len(bad_reading)<2:
                row = row[0:3] + "|random_stuff|other_problem|"
                bad_reading.append(row)
            file_content.append(row)
        
        flow_parser = DataFlowParserFactory().get_parser(file_content)        
        flow_parser = D0010Parser()
        data = flow_parser.process(file_content)
        
        for bad in bad_reading:
            for reading in data:
                self.assertNotEqual(reading['value'],bad[3])
                self.assertNotEqual(reading['raw_date'],bad[2])

        pass

    def test_parse_D0010_bad_meter(self):
        # Receive D0010 flow file with bad or malformed meters
        tmp_file_content = DataFlowFactory().get_data_flow("D0010")
        file_content = []
        for row in tmp_file_content:
            if row[0:3]=="028":
                row = row[0:3] + "||other_problem|"
            file_content.append(row)
        
        flow_parser = DataFlowParserFactory().get_parser(file_content)        
        flow_parser = D0010Parser()
        data = flow_parser.process(file_content)
        
        self.assertListEqual(data,[])
        pass

    def test_parse_D0010_bad_mpan(self):
        # Receive D0010 flow file with bad or malformed mpan
        tmp_file_content = DataFlowFactory().get_data_flow("D0010")
        file_content = []
        for row in tmp_file_content:
            if row[0:3]=="026":
                row = row[0:3] + "|1234|other_problem|"
            file_content.append(row)
        
        flow_parser = DataFlowParserFactory().get_parser(file_content)        
        flow_parser = D0010Parser()
        data = flow_parser.process(file_content)
        
        self.assertListEqual(data,[])
        pass

        # Receive D0010 flow file with not mpan
        tmp_file_content = DataFlowFactory().get_data_flow("D0010")
        file_content = []
        for row in tmp_file_content:
            if row[0:3]!="026":
                file_content.append(row)
        
        flow_parser = DataFlowParserFactory().get_parser(file_content)        
        flow_parser = D0010Parser()
        data = flow_parser.process(file_content)
        
        self.assertListEqual(data,[])
        pass

class DataFlowParserFactoryTest(TestCase):
    def test_get_parser_D0010(self):
        # Recevie D0010 flow file, get appropriate parser 
        file_content = DataFlowFactory().get_data_flow("D0010")
        
        flow_parser = DataFlowParserFactory().get_parser(file_content)
        
        self.assertIsInstance(flow_parser,BaseDataFlowParser)
        self.assertIsInstance(flow_parser,D0010Parser)
        
        pass

    def test_get_parser_basic(self):
        # Receive an unsupported DTC Flow File, should return basic parser

        # Invents a data flow on the sport and returns it
        flow_name = f"R{randint(0,9999):0>4}001"        
        file_content = DataFlowFactory().get_data_flow(flow_name)
        
        flow_parser = DataFlowParserFactory().get_parser(file_content)
        
        self.assertIs(type(flow_parser), BaseDataFlowParser)
        
        pass

    def test_bad_content(self):
        # Receive something that is not a DTC Flow file, should raise error

        file_content = [str(uuid.uuid4()) for n in range(3) ]

        with self.assertRaises(ValueError) as context:
            DataFlowParserFactory().get_parser(file_content)
        pass


######### Helper classes for testing ############

class DataFlow():
    def get(self,flow_name):
        data = [
            f"ZHV|0000475656|{flow_name}|D|UDMS|X|MRCY|20160302153151||||OPER|",
            "030|S|20160222000000|56311.0|||T|N|",
            "ZPT|0000475656|35||11|20160302154650|"
        ]
        return data
    
class D0010Flow():
    def get(self,flow_name):
        data = [
            f"ZHV|0000475656|{flow_name}002|D|UDMS|X|MRCY|20160302153151||||OPER|",
            "026|1200023305967|V|",
            "028|F75A 00802|D|",
            "030|S|20160222000000|56311.0|||T|N|",
            "026|1900001059816|V|",
            "028|S95105287|C|",
            "030|TO|20160224000000|81641.0|||T|N|",
            "026|1200033197420|V|",
            "028|L85A 28596|C|",
            "030|S|20160226000000|68902.0|||T|N|",
            "026|1200031039874|V|",
            "028|S76A 13884|C|",
            "030|S|20160226000000|17393.0|||T|N|",
            "026|1591055549625|V|",
            "028|D03L80840|C|",
            "030|A1|20160301000000|50548.0|||T|N|",
            "026|2200031930792|V|",
            "028|S85D24767|C|",
            "030|01|20160301000000|20231.0|||T|N|",
            "030|02|20160301000000|64472.0|||T|N|",
            "026|1200022664056|V|",
            "028|D03A 09936|D|",
            "030|S|20160221000000|77766.0|||T|N|",
            "026|1900005260419|V|",
            "028|D0248417|D|",
            "030|TO|20160222000000|24802.0|||T|N|",
            "026|1013044353630|V|",
            "028|S82E042896|C|",
            "030|01|20160228000000|88285.0|||T|N|",
            "026|1900005281720|V|",
            "028|36933604|D|",
            "030|DY|20160222000000|80598.0|||T|N|",
            "030|NT|20160222000000|15549.0|||T|N|",
            "026|2000055433806|V|",
            "028|D13C01717|C|",
            "030|01|20160301000000|7242.0|||T|N|",
            "ZPT|0000475656|35||11|20160302154650|"
        ]
        return data

class DataFlowFactory():
    """Returns synthetic data flow files"""
    
    def get_D0010(self):
        pass

    def get_dummy_flow(self):
        """Returns a random data flow it invents on the spot
        """
        pass

    def get_data_flow(self,flow_name):
        if flow_name == "D0010":
            return D0010Flow().get(flow_name)
        else:
            return DataFlow().get(flow_name)
        