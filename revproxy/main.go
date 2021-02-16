package main

import (
	"fmt"
	"net/http"
	"net/http/httputil"
	"net/url"

	"github.com/getlegist/versailles/revproxy/log"
)

const (
	Summarization = "http://summarization:5000/predict"
	NER = "http://ner:5000/predict"
	Categorization = "http://categorization:5000/predict"

	Port = ":8000"
)

func muxRedir(redirLocation string) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		// parse the url
		uri, _ := url.Parse(redirLocation)

		log.ProxyReq(redirLocation + r.URL.Path)

		// create the reverse proxy
		proxy := httputil.NewSingleHostReverseProxy(uri)

		// Update the headers to allow for SSL redirection
		r.URL.Host = uri.Host
		r.URL.Scheme = uri.Scheme
		r.Header.Set("X-Forwarded-Host", r.Header.Get("Host"))
		r.Host = uri.Host

		proxy.ServeHTTP(w, r)
	}
}

func main() {
	http.HandleFunc("/summarize", log.Handler(muxRedir(Summarization)))
	http.HandleFunc("/categorize", log.Handler(muxRedir(NER)))
	http.HandleFunc("/ner", log.Handler(muxRedir(Categorization)))
	http.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		fmt.Fprintf(w, "healthy")
	})

	log.SysInfo("starting server on port " + Port)
	if err := http.ListenAndServe(Port, nil); err != nil {
		log.SysPanic(err)
	}
}