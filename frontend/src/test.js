import { useState } from "react";
import TextField from "@mui/material/TextField";
const Compiler = () => {
  const [outputCode, setOutputCode] = useState("");
  const [error, setError] = useState("");
  const [PascalCode, setPascalCode] = useState("");
  const handSubmit = (e) => {
    e.preventDefault();
    const codes = { PascalCode };
    fetch("http://localhost:5000/p2c", {
      method: "POST",
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(codes),
    }).then((res) => {
      return res.json().then((response) => {
        console.log(response["error"]);
        setOutputCode(response["cCodes"]);
        setError(response["error"]);
      });
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();

    reader.onload = (event) => {
      const fileContents = event.target.result;
      setPascalCode(fileContents);
    };
    reader.readAsText(file);
  };

  return (
    <div>
      <h1 id="tittle">Pascal to C Converter</h1>
      <div className="container">
        <div className="left-panel">
          <form enctype="multipart/form-data">
            <div className="form-group">
              <label for="fileUpload">Upload Pascal file:</label>
              <input
                type="file"
                id="fileUpload"
                className="file-input"
                onChange={handleFileChange}
              />
            </div>
            <div className="form-group">
              <label for="PascalCode">Enter Pascal code here:</label>
              <div className="code-wrapper">
                <textarea
                  id="PascalCode"
                  className="code-input"
                  spellcheck="false"
                  rows="30"
                  value={PascalCode}
                  onChange={(e) => setPascalCode(e.target.value)}
                  placeholder="Enter your code here..."
                ></textarea>
              </div>
            </div>
            <div className="form-group">
              <label for="translateMode">Translation mode:</label>
              <select id="translateMode">
                <option value="manual" selected>
                  Manual
                </option>
                <option value="instant">Instant</option>
              </select>
            </div>
            <button id="submitBtn" onClick={handSubmit}>
              Translate
            </button>
          </form>
        </div>
        <div className="right-panel">
          <h2>Output:</h2>
          <TextField
            label="outputCodes"
            fullWidth
            color="success"
            focused
            multiline
            rows={1}
            // size="small"
            margin="normal"
            value={outputCode}
            id="s"
            // variant="standard"
          />
          {/* <TextField
            label="errors"
            fullWidth
            // color="success"
            focused
            multiline
            rows={1}
            // size="small"
            margin="normal"
            value={error.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
            id="s"
            // variant="standard"
          /> */}
          {/* <pre id="outputCode">{outputCode}</pre> */}
          {/* <pre id="error">{error}</pre> */}
        </div>
      </div>
    </div>
  );
};

export default Compiler;
