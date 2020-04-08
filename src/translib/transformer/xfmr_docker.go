package transformer

import (
    // "errors"
    // "strconv"
    // "strings"
    "encoding/json"
    // "translib/ocbinds"
    // "translib/tlerr"
    "translib/db"
    // "io"
    // "bytes"
    // "net"
    // "encoding/binary"
    // "github.com/openconfig/ygot/ygot"
    log "github.com/golang/glog"
    "github.com/docker/docker/client"
    "github.com/docker/docker/api/types"
    "context"
    "time"
)

func init () {
    XlateFuncBind("rpc_docker_exec", rpc_docker_exec)

}

var rpc_docker_exec RpcCallpoint = func(body []byte, dbs [db.MaxDB]*db.DB) ([]byte, error) {
    log.Info("In rpc_docker_exec")

    type Input struct {
        ContainerName string `json:"container-name"`
        Command []string `json:"command"`
    }
    var sin struct {
        SonicDockerExecInput Input `json:"sonic-docker-exec:input"`
    }
    err := json.Unmarshal(body, &sin)
    if err != nil {
        panic(err)
    }



    var result struct {
        Output struct {
              Status string `json:"response"`
              Code int32 `json:"code"`
        } `json:"sonic-docker-exec:output"`
    }

    cli, err := client.NewClientWithOpts(client.WithAPIVersionNegotiation())
    if err != nil {
        result.Output.Status = err.Error()
        return json.Marshal(&result)
    }


    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    esc := types.ExecStartCheck {
        Detach: true,
    }
    ex := types.ExecConfig {
        User: "root",
        Privileged: true,
        Detach: true,
        Cmd: sin.SonicDockerExecInput.Command,
    }
    log.Info(ex)
    id, err := cli.ContainerExecCreate(ctx, sin.SonicDockerExecInput.ContainerName, ex)
    if err != nil {
        result.Output.Status = err.Error()
        result.Output.Code = 1
    }
    err = cli.ContainerExecStart(ctx, id.ID, esc)
    if err != nil {
        result.Output.Status = err.Error()
        result.Output.Code = 1
    }

    return json.Marshal(&result)
}