package log

import (
	"net/http"

	"github.com/felixge/httpsnoop"
	"go.uber.org/zap"
)

var L *zap.Logger

func init() {
	L, _ = zap.NewProduction()
	L = L.WithOptions(zap.AddCallerSkip(1))
}

func SysPanic(err error) {
	L.Panic(err.Error(), zap.String("type", "sys"))
}

func SysInfo(info string) {
	L.Info(info, zap.String("type", "sys"))
}

func ProxyReq(targetUrl string) {
	L.Debug("proxying url", zap.String("url", targetUrl), zap.String("type", "rev_proxy"))
}

// middleware to log all requests
func Handler(req http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		m := httpsnoop.CaptureMetrics(req, w, r)
		L.Debug(
			"incoming request",
			zap.String("method", r.Method),
			zap.String("url", r.URL.String()),
			zap.Int("status code", m.Code),
			zap.Duration("duration", m.Duration),
			zap.Int64("size", m.Written),
		)
	}
}