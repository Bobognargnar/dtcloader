from common.models import File,Mpan,Meter,Reading
from traceback import format_exc
from os import path
from datetime import datetime as dt, timezone


class BaseDataFlowParser:
    """ Basic flow parser does nothing except checking the headers
    """
    
    def process(self, content):
        raise NotImplementedError(f"Parser for {self._get_flow_from_header(content[0])} is not yet available")
    
    @staticmethod
    def _get_flow_from_header(raw_header):
        """Parse ZHV header and return flow name"""
        header = raw_header.split("|")
        if header[0] != "ZHV":
            raise ValueError(f"Unsupported header {header[0]}. ZHV is required.")
        if len(header)<3:
            raise ValueError(f"Missing required fields from header: {raw_header}")

        flow_name_version = header[2]

        if len(flow_name_version)==8:
            # Remove version
            return flow_name_version[:-3]
        elif len(flow_name_version)==5:
            return flow_name_version
        else:
            raise ValueError(f"Unacceptable data flow {flow_name_version}")

class D0010Parser(BaseDataFlowParser):

    def split_mpan(self,data):
        """Split data separating for different MPAN cores"""
        res = []
        mpan = []

        for datum in data:
            row = datum.split("|")

    @staticmethod
    def _get_new_reading():
        return {"mpan":None,"meter":None,"value":None,"date":None}

    def process(self,content):
        """Parses D0010 file, extracts relevant informations and stores them in the database    
        
        If data entry does not match model, we skip it.
        """

        res = []
        header = content[0]
        footer = content[-1]
        data = content[1:-1]

        # These files are ordered! If we find a new meter or mpan, we're switching 
        reading = Reading()
        for datum in data:
            row = datum.split("|")

            # MPAN Cores
            if row[0]=='026':
                if reading.validate_mpan(row):
                    reading.set_mpan(row[1])
                else: print(f"mpan {row} not valid")
            if row[0]=='028':
                if reading.validate_meter(row):
                    reading.set_meter(row[1])
                else: print(f"meter {row} not valid")
            if row[0]=='030':
                # Bad reading is skipped
                if reading.validate_reading(row):
                    reading.set_reading(date=row[2], value=row[3])
                else: print("reading not valid")
                
            if reading.is_ready():
                reading_dict = reading.get_reading()
                #print(f"New Reading! {reading_dict["mpan"]} {reading_dict["meter"]} {reading_dict["value"]} {reading_dict["date"]}")
                res.append(reading_dict)

        return res

class DataFlowParserFactory():
    """Helper class for reading and parsing generic DTC Flow files
    """
    supported_flows = ["D0010"]

    def __init__(self,) -> None:
        pass

    def is_valid(self,file_content):
        try:
            self.get_parser(file_content)
        except Exception:
            print(format_exc())
            return False
        return True
        

    def get_parser(self,flow_content):
        """Parse header and return appropriate parser"""
        flow_name = BaseDataFlowParser()._get_flow_from_header(flow_content[0])
        if flow_name == "D0010":
            return D0010Parser()
        else:
            return BaseDataFlowParser()


class Reading():
    def __init__(self) -> None:
        self.reset()

    def reset(self):
        self._mpan = None
        self._meter = None
        self._value = None
        self._date = None
        self._raw_date = None

    def set_mpan(self,core):
        self.reset()
        self._mpan = core
    
    def set_meter(self,meter):
        self._value = None
        self._date = None
        self._raw_date = None
        self._meter = meter

    def set_reading(self,date,value):
        self._value = value

        # The documentations gave no indication of time zone! I'm assuming UTC time.
        self._date = dt.strptime(date, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)

        self._raw_date = date

    def validate_mpan(self,row):
        
        # Min lenght of the reading row
        if len(row)!=4 or len(row[1])!=13:
            return False
        
        return True

    def validate_meter(self,row):
        
        # Min lenght of the reading row
        if len(row)!=4 or len(row[1])>10 or len(row[1])==0:
            return False
        
        return True

    def validate_reading(self,row):
        
        # Min lenght of the reading row
        if (len(row)<4):
            return False

        # Try to parse date field and reading row to confirm quality
        try: 
            dt.strptime(row[2], "%Y%m%d%H%M%S")
            float(row[3])
        except:
            return False
        
        return True

    def is_ready(self):
        if (self._meter and self._mpan and self._date and self._value):
            return True
        return False

    def get_reading(self):
        res = {"mpan":self._mpan,"meter":self._meter,"value":self._value,"date":self._date, "raw_date":self._raw_date}
        return res

    
    