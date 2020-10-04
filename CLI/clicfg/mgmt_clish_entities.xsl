<?xml version="1.0"?>
<!--
Copyright 2019 Dell, Inc.  

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
--> 

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- Print the ENTITY definition string, looking at the input XML file -->
<xsl:output method ="text"/>
<xsl:template match="/">
  <xsl:for-each select="/PLATFORMMODULE/ENTITYLIST/ENTITYNAME">
&lt;!ENTITY <xsl:value-of select="."/> "<xsl:value-of select="./@value"/>"&gt;</xsl:for-each>
</xsl:template>
</xsl:stylesheet>
