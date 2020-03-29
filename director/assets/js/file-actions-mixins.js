const g_convertibleDefinitions = [
  ['application/vnd.google-apps.document', 'gdoc', 'Google Docs'],
  ['text/html', 'html', 'HTML'],
  ['text/xml+jats', 'jats', 'JATS'],
  ['application/ld+json', 'jsonld', 'JSON-LD'],
  ['application/x-ipynb+json', 'ipynb', 'Jupyter Notebook'],
  ['text/markdown', 'md', 'Markdown'],
  ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx', 'Microsoft Word'],
  ['text/rmarkdown', 'rmd', 'RMarkdown']
]

// mapping of source type to output formats
const g_targetFormats = {
  __default__: {
    main: ['docx', 'md', 'html']
  },
  'application/vnd.google-apps.document': {
    main: ['docx', 'md', 'html', 'ipynb']
  }
}

const g_fileActionsCommon = {
  props: {
    previewUrl: {
      type: String,
      required: false,
      default: ''
    },
    fileType: {
      type: String,
      required: false,
      default: ''
    },
  },
  computed: {
    hasConvertTargets () {
      return this.convertTargets.length > 0
    },
    allowPreview () {
      return this.hasConvertTargets && this.previewUrl !== ''
    },
    mainConvertTargets () {
      const convertTargets = this.convertTargets

      if (convertTargets.length === 0)
        return

      let targetCodes

      if (g_targetFormats[this.fileType] !== undefined)
        targetCodes = g_targetFormats[this.fileType].main
      else
        targetCodes = g_targetFormats.__default__.main

      return convertTargets.filter(typeDefinition => targetCodes.indexOf(typeDefinition[0]) !== -1)
    },
    convertTargets () {
      const convertibleMimetypes = g_convertibleDefinitions.map(typeDef => typeDef[0])

      if (convertibleMimetypes.indexOf(this.fileType) === -1)
        return []

      return g_convertibleDefinitions.filter(typeDefinition => typeDefinition[0] !== this.fileType).map(typeDefinition => typeDefinition.slice(1))
    }
  },
  mounted () {
    this.$root.$on('menu-hide', () => {
      this.active = false
    })
  },
  methods: {
    toggle () {
      if (this.active) {
        this.active = false
      } else {
        this.$root.$emit('menu-hide')
        this.active = true
      }
    },
  }
}