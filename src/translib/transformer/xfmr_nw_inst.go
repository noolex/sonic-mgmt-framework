package transformer

import (
    "translib/db"
    "translib/tlerr"
    log "github.com/golang/glog"
)

func init() {
    XlateFuncBind("network_instance_post_xfmr", network_instance_post_xfmr)
}

var nw_inst_del_not_allowed_map = map[string]bool {
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/confederation" : true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/confederation/config" : true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/graceful-restart" : true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/graceful-restart/config" : true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/use-multiple-paths": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/use-multiple-paths/ebgp": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/use-multiple-paths/ebgp/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/route-selection-options": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/route-selection-options/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/use-multiple-paths": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/use-multiple-paths/ebgp": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/use-multiple-paths/ebgp/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/use-multiple-paths/ibgp": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/use-multiple-paths/ibgp/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/aggregate-address-config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/network-config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/default-route-distance": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/default-route-distance/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/route-flap-damping": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/afi-safis/afi-safi/route-flap-damping/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/dynamic-neighbor-prefixes": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/logging-options": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/logging-options/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/bgp-ext-route-reflector": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/bgp-ext-route-reflector/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/global-defaults": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/global-defaults/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/update-delay": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/update-delay/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/max-med": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/global/max-med/config": true,

    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/timers": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/timers/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/transport": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/transport/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/ebgp-multihop": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/ebgp-multihop/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/add-paths": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/add-paths/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/apply-policy": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/apply-policy/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/ipv4-unicast": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/ipv4-unicast/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/ipv4-unicast/prefix-limit": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/ipv4-unicast/prefix-limit/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/ipv6-unicast": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/ipv6-unicast/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/ipv6-unicast/prefix-limit": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/ipv6-unicast/prefix-limit/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/allow-own-as": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/allow-own-as/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/attribute-unchanged": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/attribute-unchanged/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/filter-list": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/filter-list/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/next-hop-self": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/next-hop-self/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/prefix-list": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/prefix-list/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/remove-private-as": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/remove-private-as/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/capability-orf": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/afi-safis/afi-safi/capability-orf/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/enable-bfd": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor/enable-bfd/config": true,

    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/timers": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/timers/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/transport": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/transport/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/ebgp-multihop": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/ebgp-multihop/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/add-paths": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/add-paths/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/apply-policy": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/apply-policy/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/ipv4-unicast": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/ipv4-unicast/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/ipv4-unicast/prefix-limit": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/ipv4-unicast/prefix-limit/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/ipv6-unicast": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/ipv6-unicast/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/ipv6-unicast/prefix-limit": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/ipv6-unicast/prefix-limit/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/allow-own-as": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/allow-own-as/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/attribute-unchanged": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/attribute-unchanged/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/filter-list": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/filter-list/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/next-hop-self": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/next-hop-self/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/prefix-list": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/prefix-list/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/remove-private-as": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/remove-private-as/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/capability-orf": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/afi-safis/afi-safi/capability-orf/config": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/enable-bfd": true,
    "/openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/peer-groups/peer-group/enable-bfd/config": true,
}

var network_instance_post_xfmr PostXfmrFunc = func(inParams XfmrParams) (map[string]map[string]db.Value, error) {
    var err error
    retDbDataMap := (*inParams.dbDataMap)[inParams.curDb]

    if inParams.oper == DELETE {
        xpath, _ := XfmrRemoveXPATHPredicates(inParams.requestUri)
        log.Info("In Network-instance Post transformer for DELETE op ==> URI : ", inParams.requestUri, " ; XPATH : ", xpath)

        if del_not_allowed, found := nw_inst_del_not_allowed_map[xpath]; found && del_not_allowed {
            var err_str string = "Delete not allowed at this container"
            log.Info ("XPATH : ", xpath, " found !!! ", err_str)
            return retDbDataMap, tlerr.NotSupported(err_str)
        }
    }

    return retDbDataMap, err
}
