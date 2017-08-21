const GETCatalog = (callback) => {
    return fetch("http://127.0.0.1:7000/catalog")
    .then((response) => {return response.json()} )
    .then(callback);
}

export default GETCatalog;