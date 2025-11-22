// scripts/init-config-rs.js
rs.initiate(
   {
      _id: "cfg-rs",
      configsvr: true,
      members: [
         { _id: 0, host: "cfg1:27017" },
         { _id: 1, host: "cfg2:27017" }
      ]
   }
)