from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link

class switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(switch,self).__init__(*args,**kwargs)
        #self.mac_to_port = {}

    #topology discovery --> restituisce una lista di switch e una lista di link con edges e porta di inoltro da src
    #NB: bisogna probabilmente aggiungere delle funzioni che si accorgano di eventuali cambiamenti della topologia
    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        switch_list = get_switch(self.topology_api_app, None)
        switches = [switch.dp.id for switch in switch_list]
        links_list = get_link(self.topology_api_app, None)
        links = [(link.src.dpid, link.dst.dpid, {'port': link.src.port_no}) for link in links_list]

    #utilizzando un approccio proattivo non ce ne frega di mandare i pacchetti al controller
    #dunque dobbiamo definire delle regole di default ---> group table (group type FAST FAILOVER)
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def set_default_rule(self, ev):
        # install default forwarding rule
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser


        #bisogna trovare la sintassi per definire bene come vogliamo la group table (fast failover)
        """ Group table setup """
        buckets = []

        # Action Bucket: <PWD port_i , SetState(i-1)
        for port in range():
            dest_ip = self.int_to_ip_str(port)
            dest_eth = self.int_to_mac_str(port)
            dest_tcp = (port) * 100
            actions = [ofparser.OFPActionOutput(port=port)]

            buckets.append(ofparser.OFPBucket(weight=100,
                                              watch_port=ofproto.OFPP_ANY,
                                              watch_group=ofproto.OFPG_ANY,
                                              actions=actions))

        req = ofparser.OFPGroupMod(datapath=datapath,
                                   command=ofproto.OFPGC_ADD,
                                   type_=ofproto.OFPGT_SELECT,
                                   group_id=1,
                                   buckets=buckets)

        datapath.send_msg(req)
